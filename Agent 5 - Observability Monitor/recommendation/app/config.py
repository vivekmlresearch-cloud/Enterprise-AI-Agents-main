from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    clickhouse_host: str = 'localhost'
    clickhouse_port: int = 8123
    clickhouse_username: str = 'default'
    clickhouse_password: str = ''
    clickhouse_database: str = 'observability'


@lru_cache
def get_settings() -> Settings:
    return Settings()
