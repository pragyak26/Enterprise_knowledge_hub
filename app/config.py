from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Auth
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 1440
    algorithm: str = "HS256"

    # Gemini
    gemini_api_key: str = ""
    embedding_model: str = "models/gemini-embedding-001"
    chat_model: str = "gemini-2.5-flash"

    # Storage / DB
    database_url: str = "sqlite:///./data/app.db"
    storage_dir: str = "./storage"
    chroma_dir: str = "./data/chroma"

    # RAG
    chunk_size: int = 1000
    chunk_overlap: int = 150
    top_k: int = 5


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
