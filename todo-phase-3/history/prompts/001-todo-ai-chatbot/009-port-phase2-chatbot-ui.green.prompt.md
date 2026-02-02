---
id: 009
title: Port Phase 2 Chatbot UI to Phase 3
stage: green
date: 2026-02-02
surface: agent
model: claude-opus-4-5-20251101
feature: 001-todo-ai-chatbot
branch: 001-todo-ai-chatbot
user: harisawan27
command: /sp.implement
labels: ["ui", "styling", "migration", "chatbot"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - frontend/src/app/globals.css
  - frontend/src/components/ChatInterface.tsx
  - frontend/src/app/page.tsx
  - frontend/package.json
tests:
  - npm run build (PASS)
---

## Prompt

/sp.implement

**Context:**
I have already styled and customized the Chatbot UI in `todo-phase-2` to look exactly how I want.
**Goal:** I want `todo-phase-3/frontend` to match the UI/UX of the chatbot in `todo-phase-2`.

**Instructions:**
1.  **Analyze Source:** Look at `todo-phase-2/frontend` (specifically the chatbot components, page.tsx, and global CSS/Tailwind config) to understand the visual design (colors, layout, message bubbles, fonts).
2.  **Apply to Destination:** Update the `todo-phase-3/frontend` code to match this visual style.
    * Copy the `globals.css` styling rules.
    * Update the ChatKit components (or standard React components if I used custom ones) to match the message bubble design and chat container layout from Phase 2.
    * Ensure the "Agentic" backend connection in Phase 3 remains intact (do not break the API calls).

**Execution:**
Make Phase 3 look identical to Phase 2, but keep it running on the Phase 3 backend.

## Response snapshot

Successfully migrated the Phase 2 chatbot UI styling to Phase 3:

1. **Installed lucide-react** for icons (Bot, User, Sparkles, Send, Loader2, X)

2. **Updated globals.css** with Phase 2 styling:
   - CSS variables for light/dark mode (--background, --foreground, --muted, --muted-foreground)
   - Custom scrollbar styling with dark mode support
   - Keyframe animations (chat-panel-enter, fade-in, pulse-soft, slide-up, etc.)
   - Utility classes (.bg-background, .text-muted-foreground, .hover-lift, etc.)

3. **Rewrote ChatInterface.tsx** to match Phase 2's chat-widget.tsx:
   - Floating chat widget with toggle button (blue gradient with Bot icon + sparkle)
   - Chat panel with header, messages area, and input
   - AssistantAvatar and UserAvatar components with gradient backgrounds
   - User messages: blue-to-cyan gradient bubbles, right-aligned
   - Assistant messages: white/gray bubbles with borders, left-aligned
   - Loading indicator with three bouncing blue dots + "Thinking..." text
   - Rounded input with gradient send button
   - Footer text "DoneKaro AI • Get things done faster"

4. **Updated page.tsx** with landing page content behind the widget

5. **Preserved Phase 3 backend integration:**
   - API calls via `sendMessage` from `@/lib/api.ts`
   - API URL: `http://localhost:8001`
   - Endpoint: `POST /api/{userId}/chat`
   - Conversation ID persistence for context

Build verified successfully with `npm run build`.

## Outcome

- ✅ Impact: Phase 3 frontend now has identical UI/UX to Phase 2's polished chatbot design
- 🧪 Tests: npm run build passed successfully
- 📁 Files: 4 files modified (globals.css, ChatInterface.tsx, page.tsx, package.json)
- 🔁 Next prompts: Test the chatbot visually, verify dark mode support works
- 🧠 Reflection: The key was analyzing both codebases in parallel to understand the styling approach (Phase 2) and API integration (Phase 3), then merging them carefully

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Build PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Visual testing in browser to confirm styling matches exactly
