from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.task import Task as TaskModel
from app.schemas.task import DownloadYouTube, DownloadWget, TaskResponse, DownloadStatus

router = APIRouter()


@router.post("/youtube", response_model=TaskResponse)
async def download_youtube(
    download_data: DownloadYouTube,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download video/audio from YouTube"""
    # Create task
    task_id = str(uuid.uuid4())
    task = TaskModel(
        id=task_id,
        user_id=current_user.id,
        type="download_youtube",
        status="pending",
        input_data={
            "url": download_data.url,
            "audio_only": download_data.audio_only,
            "destination": download_data.destination,
            "format": download_data.format
        }
    )
    db.add(task)
    db.commit()

    # TODO: Start background task using yt-dlp

    return TaskResponse(
        task_id=task_id,
        status="pending",
        progress=0
    )


@router.post("/wget", response_model=TaskResponse)
async def download_wget(
    download_data: DownloadWget,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download file from URL"""
    # Create task
    task_id = str(uuid.uuid4())
    task = TaskModel(
        id=task_id,
        user_id=current_user.id,
        type="download_wget",
        status="pending",
        input_data={
            "url": download_data.url,
            "destination": download_data.destination,
            "filename": download_data.filename
        }
    )
    db.add(task)
    db.commit()

    # TODO: Start background task using httpx or wget

    return TaskResponse(
        task_id=task_id,
        status="pending",
        progress=0
    )


@router.get("/status/{task_id}", response_model=DownloadStatus)
async def get_download_status(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get download task status"""
    task = db.query(TaskModel).filter(
        TaskModel.id == task_id,
        TaskModel.user_id == current_user.id
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    result = task.output_data or {}

    return DownloadStatus(
        status=task.status,
        progress=task.progress,
        result=result,
        error=task.error,
        speed=result.get("speed"),
        eta=result.get("eta"),
        filename=result.get("filename")
    )


@router.delete("/{task_id}")
async def cancel_download(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel download task"""
    task = db.query(TaskModel).filter(
        TaskModel.id == task_id,
        TaskModel.user_id == current_user.id
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.status in ["completed", "failed"]:
        raise HTTPException(status_code=400, detail="Task already finished")

    # TODO: Cancel background task
    task.status = "failed"
    task.error = "Cancelled by user"
    db.commit()

    return {"message": "Download cancelled"}
