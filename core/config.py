from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from dotenv import load_dotenv
import os

# Explicitly load .env for safety
load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Point Calculator API"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: Optional[str] = None
    LOCAL_DATABASE_URL: Optional[str] = None
    
    @property
    def ASYNC_DATABASE_URL(self) -> str:
        """Get the database URL based on environment."""
        # In production (e.g., Vercel), use DATABASE_URL (Neon)
        # In local development, use LOCAL_DATABASE_URL
        url = self.DATABASE_URL if os.getenv("VERCEL") or os.getenv("PROD") else self.LOCAL_DATABASE_URL
        if not url:
            # Fallback if none are set
            return "postgresql://postgres:postgres@localhost:5432/point_calculator"
        
        # SQLAlchemy requires 'postgresql://' instead of 'postgres://' for some versions/dialects
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return url

    # Authentication
    JWT_SECRET: str = "5e81abd25315c172ee9ddc886548f7d0"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200
    
    # Legacy Supabase (to be removed)
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "https://point-calculator-flame.vercel.app",
        "https://point-calculator.vercel.app",
        "https://point-calculator-flame.vercel.app/rules",
    ]

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()
