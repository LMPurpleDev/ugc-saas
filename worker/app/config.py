import os
from typing import Optional

class Settings:
    # Database
    mongodb_url: str = os.getenv("MONGODB_URL", "mongodb://mongo:27017")
    database_name: str = os.getenv("DATABASE_NAME", "ugc_saas")
    
    # Redis (for Celery)
    redis_url: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    
    # Instagram API
    instagram_app_id: Optional[str] = os.getenv("INSTAGRAM_APP_ID")
    instagram_app_secret: Optional[str] = os.getenv("INSTAGRAM_APP_SECRET")
    
    # OpenAI
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # Email
    sendgrid_api_key: Optional[str] = os.getenv("SENDGRID_API_KEY")
    from_email: str = os.getenv("FROM_EMAIL", "noreply@ugcsaas.com")
    
    # Reports
    reports_dir: str = os.getenv("REPORTS_DIR", "/app/reports")

settings = Settings()

