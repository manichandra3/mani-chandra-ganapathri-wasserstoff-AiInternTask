from pydantic_settings import BaseSettings
from typing import Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    PROJECT_NAME: str = "Document Processing API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # File storage settings
    UPLOAD_DIR: Path = Path("data/uploads")
    PROCESSED_DIR: Path = Path("data/processed")
    
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    
    # OCR settings
    TESSERACT_CMD: Optional[str] = None
    
    # API Keys
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")
    
    class Config:
        case_sensitive = True
        env_file = ".env"

# Instantiate settings
settings = Settings()

# Create necessary directories
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# Auto-configure Tesseract on Windows if not provided
if os.name == 'nt' and not settings.TESSERACT_CMD:
    settings.TESSERACT_CMD = os.getenv("TESSERACT_CMD")
