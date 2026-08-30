from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_name: str = 'research-assistant-agent'
    log_level: str = 'INFO'

    qdrant_url: str = 'http://qdrant:6333'
    qdrant_collection: str = 'papers'
    vector_size: int = 1024
    top_k: int = 8

    llm_base_url: str = 'http://host.docker.internal:9000/v1'
    llm_api_key: str = 'change-me'
    llm_model: str = 'nemotron'

    embedding_base_url: str = 'http://host.docker.internal:9001/v1'
    embedding_api_key: str = 'change-me'
    embedding_model: str = 'nvidia/nv-embedqa-e5-v5'

    rerank_base_url: str = 'http://host.docker.internal:9002/v1'
    rerank_api_key: str = 'change-me'
    rerank_model: str = 'nvidia/nv-rerankqa-mistral-4b-v3'

    arxiv_api_url: str = 'http://export.arxiv.org/api/query'
    semantic_scholar_api_url: str = 'https://api.semanticscholar.org/graph/v1'
    semantic_scholar_api_key: str = ''
    crossref_api_url: str = 'https://api.crossref.org/works'
    user_agent: str = 'research-agent/1.0'

    benchmark_concurrency: int = 4
    benchmark_requests: int = 20

    mcp_host: str = '0.0.0.0'
    mcp_port: int = 8080


settings = Settings()
