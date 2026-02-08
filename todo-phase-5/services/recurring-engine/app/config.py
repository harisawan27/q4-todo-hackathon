"""Recurring engine configuration."""

import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    service_name: str = os.environ.get("SERVICE_NAME", "recurring-engine")
    log_level: str = os.environ.get("LOG_LEVEL", "INFO")
    dapr_http_port: int = int(os.environ.get("DAPR_HTTP_PORT", "3502"))
    host: str = "0.0.0.0"
    port: int = 8002


settings = Settings()
