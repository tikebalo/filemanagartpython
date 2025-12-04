from pydantic import BaseModel
from typing import Optional, Dict, List


class ConvertAudio(BaseModel):
    input_path: str
    output_format: str
    quality: str = "high"  # low, medium, high


class ConvertImage(BaseModel):
    input_path: str
    output_format: str
    quality: int = 90


class DownloadYouTube(BaseModel):
    url: str
    audio_only: bool = False
    destination: str = "/"
    format: str = "mp4"


class DownloadWget(BaseModel):
    url: str
    destination: str = "/"
    filename: Optional[str] = None


class TaskResponse(BaseModel):
    task_id: str
    status: str
    progress: int = 0


class TaskStatus(BaseModel):
    status: str
    progress: int
    result: Optional[Dict] = None
    error: Optional[str] = None


class ConvertFormatsResponse(BaseModel):
    audio: List[str]
    image: List[str]


class DownloadStatus(TaskStatus):
    speed: Optional[str] = None
    eta: Optional[str] = None
    filename: Optional[str] = None
