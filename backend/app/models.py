from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime

class QueryRequest(BaseModel):
    question: str
    top_k: Optional[int] = 10

class Source(BaseModel):
    type: str  # "pdf", "word", "excel"
    filename: str
    content: Optional[str] = None
    metadata: Optional[Dict] = None

class QueryResponse(BaseModel):
    answer: str
    sources: List[Source]
    processing_time: float

class UploadResponse(BaseModel):
    filename: str
    status: str
    message: str
    timestamp: datetime

class DocumentInfo(BaseModel):
    filename: str
    type: str
    size: int
    upload_date: datetime
    indexed: bool

class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    username: str