from pydantic import BaseModel
from typing import Dict, List
from datetime import datetime


class SystemStats(BaseModel):
    disk_total: int
    disk_used: int
    disk_free: int
    memory_total: int
    memory_used: int
    cpu_percent: float
    uptime: str


class StorageByType(BaseModel):
    count: int
    size: int


class StorageStats(BaseModel):
    total_files: int
    total_size: int
    by_type: Dict[str, StorageByType]


class UserStats(BaseModel):
    username: str
    used: int
    quota: int
    percent: float


class AdminStatsResponse(BaseModel):
    system: SystemStats
    storage: StorageStats
    users_stats: List[UserStats]


class ActivityLog(BaseModel):
    id: int
    user: str
    action: str
    details: str
    ip: str
    timestamp: datetime

    class Config:
        from_attributes = True


class ActivityResponse(BaseModel):
    activities: List[ActivityLog]
