from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "Point Calculator API"
    API_V1_STR: str = "/api/v1"
    
    SUPABASE_URL: Optional[str] = os.getenv("SUPABASE_URL")
    SUPABASE_KEY: Optional[str] = os.getenv("SUPABASE_KEY")
    SUPABASE_DB_PASSWORD: Optional[str] = os.getenv("SUPABASE_DB_PASSWORD")
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()
