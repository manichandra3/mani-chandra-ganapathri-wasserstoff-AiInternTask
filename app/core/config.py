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
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./data/documents.db")
    
    # OCR settings
    TESSERACT_CMD: Optional[str] = None  # Will be set based on OS
    
    # OpenAI API key
    OPENAI_API_KEY: str = ""
    
    # Gemini API key
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "AIzaSyDk48D8bxceLXT29GPw96yKKSENT_uK8x8")
    
    class Config:
        case_sensitive = True
        env_file = ".env"

# Create directories if they don't exist
settings = Settings()
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# Set Tesseract path based on OS
if os.name == 'nt':  # Windows
    settings.TESSERACT_CMD = r'C:\Program Files\Tesseract-OCR\tesseract.exe' 