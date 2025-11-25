from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class FileItem(BaseModel):
    name: str
    type: str  # file or folder
    path: str
    size: Optional[int] = None
    mime: Optional[str] = None
    modified: datetime
    thumbnail: Optional[str] = None
    is_favorite: bool = False
    items_count: Optional[int] = None  # For folders


class FileListResponse(BaseModel):
    items: List[FileItem]
    path: str
    parent: Optional[str]
    total_size: int


class FileUploadResponse(BaseModel):
    uploaded: List[str]
    errors: List[dict]


class FileRename(BaseModel):
    path: str
    new_name: str


class FileMove(BaseModel):
    paths: List[str]
    destination: str


class FileCopy(BaseModel):
    paths: List[str]
    destination: str


class FileSearch(BaseModel):
    query: str
    path: str = "/"
    recursive: bool = True


class FolderCreate(BaseModel):
    path: str
    name: str


class ArchiveCreate(BaseModel):
    paths: List[str]
    archive_name: str
    format: str = Field(..., pattern="^(zip|tar|tar.gz)$")


class ArchiveExtract(BaseModel):
    archive_path: str
    destination: str


class FavoriteAdd(BaseModel):
    path: str


class TrashItem(BaseModel):
    id: int
    original_path: str
    deleted_at: datetime
    expires_at: datetime
    size: int

    class Config:
        from_attributes = True


class TrashResponse(BaseModel):
    items: List[TrashItem]
    total_size: int


class TrashRestore(BaseModel):
    ids: List[int]
