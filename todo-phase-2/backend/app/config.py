"""Configuration management using pydantic-settings"""

from functools import lru_cache

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

    # Authentication (shared with Better-Auth frontend)
    better_auth_secret: str

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    # Email Configuration (Resend API - simple & free)
    # Get your API key from https://resend.com (free: 100 emails/day)
    resend_api_key: str = ""
    email_from: str = "DoneKaro <onboarding@resend.dev>"  # Use your domain after verification
    email_enabled: bool = True

    # Notification Settings
    deadline_reminder_hours: int = 24  # Send reminder X hours before deadline
    scheduler_enabled: bool = True

    # Web Push (VAPID) Settings
    # Generate with: npx web-push generate-vapid-keys
    vapid_public_key: str = ""
    vapid_private_key: str = ""
    vapid_email: str = "admin@donekaro.com"
    push_enabled: bool = False

    # Firebase Cloud Messaging (FCM) Settings
    # Download service account JSON from Firebase Console > Project Settings > Service Accounts
    fcm_credentials_json: str = ""  # JSON string of service account credentials
    fcm_enabled: bool = True

    # AI Chatbot Settings (LiteLLM + Gemini)
    gemini_api_key: str = ""
    llm_model: str = "gemini/gemini-2.5-flash"
    chatbot_enabled: bool = True


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
