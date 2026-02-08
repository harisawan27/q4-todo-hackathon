"""Dapr Secrets API wrapper for credential management."""

from app import dapr_client


async def get_secret(secret_name: str) -> dict[str, str]:
    """Get a secret from the configured Dapr secret store."""
    return await dapr_client.get_secret(secret_name)


async def get_gemini_api_key() -> str:
    """Get the Gemini API key."""
    secrets = await dapr_client.get_secret("gemini-api-key")
    return secrets["gemini-api-key"]


async def get_jwt_secret() -> str:
    """Get the JWT validation secret."""
    secrets = await dapr_client.get_secret("jwt-secret")
    return secrets["jwt-secret"]
