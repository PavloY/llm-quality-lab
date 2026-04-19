from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    llm_api_key: str = ""
    llm_base_url: str = "https://api.openai.com/v1"
    llm_model: str = "gpt-4o-mini"
    qdrant_path: str = "./qdrant_data"
    embedding_model: str = "all-MiniLM-L6-v2"

    model_config = {"env_file": ".env"}


settings = Settings()
