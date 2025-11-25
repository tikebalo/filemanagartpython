from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ShareCreate(BaseModel):
    path: str
    expires_in: Optional[int] = None  # Seconds
    password: Optional[str] = None
    max_downloads: Optional[int] = None


class ShareResponse(BaseModel):
    id: str
    path: str
    url: str
    created_at: datetime
    expires_at: Optional[datetime]
    max_downloads: Optional[int]
    download_count: int
    has_password: bool

    class Config:
        from_attributes = True


class SharePublicResponse(BaseModel):
    items: List[dict]
    path: str
    is_password_protected: bool


class SharePasswordVerify(BaseModel):
    password: str
