"""Application configuration using Pydantic Settings"""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Database
    database_url: str

    # LLM Configuration
    # Gemini API Key (primary - for Google Gemini models via LiteLLM)
    gemini_api_key: Optional[str] = None

    # OpenAI API Key (fallback - kept for compatibility)
    openai_api_key: Optional[str] = None

    # Model selection (default to Gemini 2.5 Flash)
    # Available models: gemini-2.5-flash, gemini-2.5-flash-lite, gpt-4o-mini
    llm_model: str = "gemini/gemini-2.5-flash"


# Global settings instance
settings = Settings()
