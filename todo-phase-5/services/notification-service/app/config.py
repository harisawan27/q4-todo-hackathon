"""Notification service configuration."""

import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    service_name: str = os.environ.get("SERVICE_NAME", "notification-service")
    log_level: str = os.environ.get("LOG_LEVEL", "INFO")
    dapr_http_port: int = int(os.environ.get("DAPR_HTTP_PORT", "3501"))
    host: str = "0.0.0.0"
    port: int = 8001


settings = Settings()
