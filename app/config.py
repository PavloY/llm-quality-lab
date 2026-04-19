from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    llm_api_key: str = ""
    llm_base_url: str = "https://openrouter.ai/api/v1"
    llm_model: str = "qwen/qwen-2.5-72b-instruct"
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    embedding_model: str = "all-MiniLM-L6-v2"

    model_config = {"env_file": ".env"}


settings = Settings()
