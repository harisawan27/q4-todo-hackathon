"""LiteLLM agent runner for conversational task management."""

import json
import logging
from typing import Optional

import litellm

from app.chatbot.tools import TOOL_DEFINITIONS, TOOL_MAP, set_current_user
from app.models.conversation import ConversationContext, MessageRole
from app.services import state_service

logger = logging.getLogger("chat-api")

SYSTEM_PROMPT = """You are DoneKaro, a helpful task management assistant. You help users manage their tasks through natural conversation.

You can:
- Create tasks with titles, descriptions, priorities, due dates, and tags
- List all tasks
- Complete tasks by title
- Update task details (title, description, priority)
- Delete tasks by title
- Find tasks by title

When users ask to create tasks, extract the title and any optional details (priority, due date, tags, description).
When users mention completing, finishing, or doing a task, use the complete_task tool.
When users want to see their tasks, use list_tasks.

Be conversational, helpful, and concise. Confirm actions taken.
If a request is unclear, ask for clarification rather than guessing."""


async def _load_or_create_conversation(
    user_id: str, conversation_id: Optional[str] = None
) -> ConversationContext:
    """Load existing conversation or create a new one."""
    if conversation_id:
        result = await state_service.get_task(f"conversation--{conversation_id}")
        # Note: reusing get_task's state access pattern for conversation
        from app import dapr_client
        data, _ = await dapr_client.get_state(f"conversation--{conversation_id}")
        if data:
            return ConversationContext(**data)

    return ConversationContext(user_id=user_id)


async def _save_conversation(conversation: ConversationContext) -> None:
    """Save conversation context to Dapr state with TTL."""
    from app import dapr_client
    await dapr_client.save_state([{
        "key": f"conversation--{conversation.id}",
        "value": conversation.model_dump(mode="json"),
        "metadata": {"ttlInSeconds": "14400"},  # 4 hours
    }])


async def process_message(
    user_id: str,
    message: str,
    conversation_id: Optional[str] = None,
) -> dict:
    """Process a user message through the LiteLLM agent."""
    set_current_user(user_id)

    conversation = await _load_or_create_conversation(user_id, conversation_id)
    conversation.add_message(MessageRole.USER, message)

    # Build messages for LiteLLM
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in conversation.messages:
        messages.append({"role": msg.role.value, "content": msg.content})

    task_action = None

    try:
        # Load Gemini API key
        from app.services.secret_service import get_gemini_api_key
        api_key = await get_gemini_api_key()

        max_iterations = 5
        for _ in range(max_iterations):
            response = await litellm.acompletion(
                model="gemini/gemini-2.0-flash",
                messages=messages,
                tools=TOOL_DEFINITIONS,
                tool_choice="auto",
                api_key=api_key,
            )

            choice = response.choices[0]

            if choice.finish_reason == "tool_calls" and choice.message.tool_calls:
                # Process tool calls
                messages.append(choice.message.model_dump())

                for tool_call in choice.message.tool_calls:
                    func_name = tool_call.function.name
                    func_args = json.loads(tool_call.function.arguments)

                    logger.info(f"Tool call: {func_name}({func_args})")

                    if func_name in TOOL_MAP:
                        result = await TOOL_MAP[func_name](**func_args)
                        result_data = json.loads(result)

                        # Track task action for response
                        if result_data.get("status") in ("created", "updated", "completed", "deleted"):
                            task_action = {
                                "action": result_data["status"],
                                "task_id": result_data.get("task_id"),
                                "task_title": result_data.get("title"),
                            }
                        elif result_data.get("status") == "success" and "tasks" in result_data:
                            task_action = {"action": "listed"}
                    else:
                        result = json.dumps({"error": f"Unknown function: {func_name}"})

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result,
                    })
            else:
                # Final text response
                assistant_message = choice.message.content or ""

                # Edge case: LLM returned no tool calls and no clear response
                # Provide a helpful clarification prompt instead of an empty/generic reply
                if not assistant_message.strip() or (
                    not task_action
                    and not choice.message.tool_calls
                    and len(assistant_message.strip()) < 10
                ):
                    assistant_message = (
                        "I'm not sure what you mean. I can help you manage tasks "
                        "-- try saying things like 'Add a task to buy groceries' "
                        "or 'Show my tasks'."
                    )

                conversation.add_message(MessageRole.ASSISTANT, assistant_message)
                await _save_conversation(conversation)

                return {
                    "response": assistant_message,
                    "conversation_id": conversation.id,
                    "task_action": task_action,
                }

        # Exceeded max iterations
        fallback = "I've completed the requested operations."
        conversation.add_message(MessageRole.ASSISTANT, fallback)
        await _save_conversation(conversation)

        return {
            "response": fallback,
            "conversation_id": conversation.id,
            "task_action": task_action,
        }

    except Exception as e:
        logger.error(f"Agent runner error: {e}", exc_info=True)
        error_msg = "I encountered an issue processing your request. Please try again."
        conversation.add_message(MessageRole.ASSISTANT, error_msg)
        await _save_conversation(conversation)

        return {
            "response": error_msg,
            "conversation_id": conversation.id,
            "task_action": None,
        }
