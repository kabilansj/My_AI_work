"""Backend configuration using Pydantic Settings."""

import os
from pathlib import Path
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"

# Ensure runtime directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


class Settings(BaseModel):
    app_name: str = "Clinical Intelligence & Extraction Platform"
    version: str = "1.0.0"
    debug: bool = True

    # Database: Defaults to local SQLite, or PostgreSQL if DATABASE_URL is set
    database_url: str = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{DATA_DIR}/clinical_platform.db"
    )

    # Gemini / AI settings
    gemini_api_key: str = os.environ.get("GEMINI_API_KEY", "")
    default_engine: str = os.environ.get("EXTRACTION_ENGINE", "auto")  # "auto", "local", "llm"

    # CORS
    cors_origins: list = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://localhost:8000",
        "*"
    ]


settings = Settings()
