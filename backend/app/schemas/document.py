"""Pydantic schemas for Document operations."""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict


class DocumentCreateText(BaseModel):
    filename: str = "clinical_note.txt"
    content: str


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    filename: str
    mime_type: str
    raw_text: str
    created_at: datetime
