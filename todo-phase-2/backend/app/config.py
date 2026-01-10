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

    # Email Configuration (SMTP)
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from_email: str = ""
    smtp_from_name: str = "Todo App"
    email_enabled: bool = False

    # Notification Settings
    deadline_reminder_hours: int = 24  # Send reminder X hours before deadline
    scheduler_enabled: bool = True


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
