from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./civicpulse.db"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REDIS_URL: str = "redis://localhost:6379"
    AI_API_KEY: Optional[str] = None
    AI_API_ENDPOINT: Optional[str] = None
    S3_BUCKET: Optional[str] = None
    S3_ENDPOINT: Optional[str] = None
    
    class Config:
        env_file = ".env"

settings = Settings()
