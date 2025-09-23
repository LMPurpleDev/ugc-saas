from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Database
    mongodb_url: str = "mongodb://mongo:27017"
    database_name: str = "ugc_saas"
    
    # JWT
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # Instagram API
    instagram_app_id: Optional[str] = None
    instagram_app_secret: Optional[str] = None
    instagram_redirect_uri: str = "http://localhost:3000/auth/instagram/callback"
    
    # OpenAI
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # Email
    sendgrid_api_key: Optional[str] = None
    from_email: str = "noreply@ugcsaas.com"
    
    # Redis (for Celery)
    redis_url: str = "redis://redis:6379/0"
    
    # CORS
    allowed_origins: list = ["http://localhost:3000", "http://frontend:3000"]
    
    class Config:
        env_file = ".env"

settings = Settings()

