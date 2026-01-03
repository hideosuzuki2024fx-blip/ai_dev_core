"""
Pydantic schemas define the request and response structures for the API.
Keeping them separate from ORM models decouples validation from
persistence.  When adding new endpoints or fields, update these
schemas accordingly.
"""

from typing import List, Optional, Dict
from datetime import datetime
from pydantic import BaseModel, Field


class RewriteRequest(BaseModel):
    text: str = Field(..., description="Original text provided by the user")


class RewriteOption(BaseModel):
    text: str
    reason: str
    emotion: str


class RewriteResponse(BaseModel):
    original: str
    options: List[RewriteOption]
    history_id: int


class EmotionRequest(BaseModel):
    text: str


class EmotionResponse(BaseModel):
    emotion: str


class SaveHistoryRequest(BaseModel):
    history_id: int
    selected_option: int


class HistoryResponse(BaseModel):
    message: str


class HistoryDetail(BaseModel):
    id: int
    original: str
    rewrites: List[str]
    sentiments: List[str]
    selected_option: Optional[int]
    created_at: datetime