from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "AI PPT Generator"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    DATABASE_URL: str = "sqlite+aiosqlite:///./ai_ppt_v2.db"
    DATABASE_URL_SYNC: str = "sqlite:///./ai_ppt_v2.db"
    
    REDIS_URL: str = "redis://localhost:6379/0"
    
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_DAYS: int = 7
    
    DASHSCOPE_API_KEY: Optional[str] = None
    MOONSHOT_API_KEY: Optional[str] = None
    
    OSS_ACCESS_KEY_ID: Optional[str] = None
    OSS_ACCESS_KEY_SECRET: Optional[str] = None
    OSS_ENDPOINT: str = "https://oss-cn-hangzhou.aliyuncs.com"
    OSS_BUCKET_NAME: str = "ai-ppt-files"
    
    FREE_USER_DAILY_LIMIT: int = 3
    FREE_USER_STORAGE_LIMIT: int = 5
    MEMBER_STORAGE_LIMIT: int = 10240
    
    MONTHLY_MEMBERSHIP_PRICE: float = 39.0
    QUARTERLY_MEMBERSHIP_PRICE: float = 99.0
    YEARLY_MEMBERSHIP_PRICE: float = 299.0
    
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
