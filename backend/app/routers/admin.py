from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import psutil
from datetime import datetime, timedelta

from app.database import get_db
from app.dependencies import get_current_admin
from app.models.user import User
from app.models.activity import Activity
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.schemas.stats import AdminStatsResponse, SystemStats, StorageStats, StorageByType, UserStats, ActivityResponse, ActivityLog
from app.utils.security import hash_password
from app.utils.files import get_user_storage_path, get_directory_size, get_file_category, get_file_mime_type
from pathlib import Path
from app.config import settings

router = APIRouter()


@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all users (admin only)"""
    users = db.query(User).all()
    return [UserResponse.from_orm(user) for user in users]


@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create new user (admin only)"""
    # Check if user exists
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")

    user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hash_password(user_data.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return UserResponse.from_orm(user)


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: dict,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update user (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if "quota" in user_data:
        user.quota = user_data["quota"]
    if "role" in user_data:
        user.role = user_data["role"]

    db.commit()
    db.refresh(user)

    return UserResponse.from_orm(user)


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Delete user (admin only)"""
    if user_id == current_admin.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # TODO: Delete user's files
    db.delete(user)
    db.commit()

    return {"message": "User deleted"}


@router.get("/stats", response_model=AdminStatsResponse)
async def get_system_stats(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get system statistics (admin only)"""
    # System stats
    disk = psutil.disk_usage('/')
    memory = psutil.virtual_memory()
    cpu_percent = psutil.cpu_percent(interval=1)

    # Uptime
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    uptime = datetime.now() - boot_time
    uptime_str = str(uptime).split('.')[0]

    system_stats = SystemStats(
        disk_total=disk.total,
        disk_used=disk.used,
        disk_free=disk.free,
        memory_total=memory.total,
        memory_used=memory.used,
        cpu_percent=cpu_percent,
        uptime=uptime_str
    )

    # Storage stats
    storage_path = Path(settings.STORAGE_PATH)
    total_files = 0
    total_size = 0
    by_type = {}

    for user_dir in (storage_path / "users").iterdir():
        if user_dir.is_dir():
            for file_path in user_dir.rglob('*'):
                if file_path.is_file():
                    total_files += 1
                    size = file_path.stat().st_size
                    total_size += size

                    mime_type = get_file_mime_type(file_path)
                    category = get_file_category(mime_type)

                    if category not in by_type:
                        by_type[category] = StorageByType(count=0, size=0)

                    by_type[category].count += 1
                    by_type[category].size += size

    storage_stats = StorageStats(
        total_files=total_files,
        total_size=total_size,
        by_type=by_type
    )

    # User stats
    users = db.query(User).all()
    users_stats = []
    for user in users:
        user_storage = get_user_storage_path(user.username)
        used = get_directory_size(user_storage)
        percent = (used / user.quota * 100) if user.quota > 0 else 0

        users_stats.append(UserStats(
            username=user.username,
            used=used,
            quota=user.quota,
            percent=round(percent, 2)
        ))

    return AdminStatsResponse(
        system=system_stats,
        storage=storage_stats,
        users_stats=users_stats
    )


@router.get("/activity", response_model=ActivityResponse)
async def get_activity_log(
    limit: int = Query(100, le=1000),
    user: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get activity log (admin only)"""
    query = db.query(Activity).join(User)

    if user:
        query = query.filter(User.username == user)
    if action:
        query = query.filter(Activity.action == action)

    activities = query.order_by(Activity.timestamp.desc()).limit(limit).all()

    return ActivityResponse(
        activities=[
            ActivityLog(
                id=act.id,
                user=act.user.username,
                action=act.action,
                details=act.details or "",
                ip=act.ip_address or "",
                timestamp=act.timestamp
            )
            for act in activities
        ]
    )
