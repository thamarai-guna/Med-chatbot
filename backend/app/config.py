from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/med_chatbot"
    
    # JWT
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Edge Device Authentication
    EDGE_DEVICE_API_KEY: str = "edge-device-secret-key-change-in-production"
    
    # Application
    APP_NAME: str = "Med-Chatbot Hospital Platform"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
