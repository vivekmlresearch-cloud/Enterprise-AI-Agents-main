from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = Field(default="local", alias="APP_ENV")
    db_url: str = Field(default="sqlite:///./finance_agent.db", alias="DB_URL")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    email_enabled: bool = Field(default=False, alias="EMAIL_ENABLED")
    email_host: str = Field(default="", alias="EMAIL_HOST")
    email_port: int = Field(default=587, alias="EMAIL_PORT")
    email_username: str = Field(default="", alias="EMAIL_USERNAME")
    email_password: str = Field(default="", alias="EMAIL_PASSWORD")
    email_from: str = Field(default="", alias="EMAIL_FROM")
    email_to: str = Field(default="", alias="EMAIL_TO")

    news_lookback_days: int = Field(default=5, alias="NEWS_LOOKBACK_DAYS")
    index_symbols: str = Field(default="^NSEI,^BSESN", alias="INDEX_SYMBOLS")

    llm_provider: str = Field(default="mock", alias="LLM_PROVIDER")
    macro_model_name: str = Field(default="gemma-4-e4b-instruct", alias="MACRO_MODEL_NAME")
    judge_model_name: str = Field(default="gemma-4-31b-instruct", alias="JUDGE_MODEL_NAME")
    openai_compatible_base_url: str = Field(default="http://localhost:8000/v1", alias="OPENAI_COMPATIBLE_BASE_URL")
    openai_compatible_api_key: str = Field(default="dummy", alias="OPENAI_COMPATIBLE_API_KEY")
    google_cloud_project: str = Field(default="", alias="GOOGLE_CLOUD_PROJECT")
    google_cloud_location: str = Field(default="us-central1", alias="GOOGLE_CLOUD_LOCATION")
    vertex_gemma_endpoint_id: str = Field(default="", alias="VERTEX_GEMMA_ENDPOINT_ID")

    enable_presidio: bool = Field(default=True, alias="ENABLE_PRESIDIO")
    send_email_only_for_buy: bool = Field(default=False, alias="SEND_EMAIL_ONLY_FOR_BUY")
    buy_threshold: int = Field(default=70, alias="BUY_THRESHOLD")
    watch_threshold: int = Field(default=55, alias="WATCH_THRESHOLD")


settings = Settings()
