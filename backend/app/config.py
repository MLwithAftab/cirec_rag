from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # API Keys
    groq_api_key: str
    
    # Security
    admin_username: str
    admin_password: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    
    # Paths
    upload_dir: str = "data/uploads"
    vector_db_dir: str = "data/vector_db"
    
    # Model Settings
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    llm_model: str = "llama-3.3-70b-versatile"
    chunk_size: int = 4096
    chunk_overlap: int = 200
    top_k: int = 10
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()