from pydantic_settings import BaseSettings
from typing import Optional, Literal

class Settings(BaseSettings):
    # API Keys
    SILICONFLOW_API_KEY: str
    SEARCH1API_KEY: str
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./chat_history.db"
    
    # API Settings
    SILICONFLOW_API_URL: str = "https://api.siliconflow.com/v1/chat/completions"
    SEARCH1API_URL: str = "https://api.search1api.com/search"
    
    # Default Model
    DEFAULT_MODEL: str = "Pro/deepseek-ai/DeepSeek-R1"  # 使用 Pro 版本的 DeepSeek R1 作为默认模型
    
    # App Settings
    APP_NAME: str = "Personal Knowledge Assistant"
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings() 