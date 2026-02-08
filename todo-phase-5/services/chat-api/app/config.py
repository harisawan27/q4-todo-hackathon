"""Application configuration using environment variables and Dapr Secrets."""

import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    service_name: str = os.environ.get("SERVICE_NAME", "chat-api")
    log_level: str = os.environ.get("LOG_LEVEL", "INFO")
    dapr_http_port: int = int(os.environ.get("DAPR_HTTP_PORT", "3500"))
    host: str = "0.0.0.0"
    port: int = 8000


settings = Settings()
