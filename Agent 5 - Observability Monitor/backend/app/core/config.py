from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    app_name: str = 'Observability AI Agent'
    app_env: str = 'development'
    api_host: str = '0.0.0.0'
    api_port: int = 8000
    cors_origins: str = 'http://localhost:3000'

    clickhouse_host: str = 'localhost'
    clickhouse_port: int = 8123
    clickhouse_username: str = 'default'
    clickhouse_password: str = ''
    clickhouse_database: str = 'observability'

    vllm_base_url: str = 'http://localhost:8001/v1'
    vllm_api_key: str = 'local-dev-key'
    vllm_model: str = 'meta-llama/Meta-Llama-3-8B-Instruct'

    temporal_host: str = 'localhost:7233'
    temporal_namespace: str = 'default'

    smtp_host: str = 'localhost'
    smtp_port: int = 1025
    smtp_from: str = 'alerts@example.com'

    slack_webhook_url: str | None = None
    pagerduty_integration_key: str | None = None

    @field_validator('cors_origins')
    @classmethod
    def normalize_origins(cls, value: str) -> str:
        return value

    @property
    def cors_origin_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(',') if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
