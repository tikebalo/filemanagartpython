from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.task import Task as TaskModel
from app.schemas.task import ConvertAudio, ConvertImage, TaskResponse, TaskStatus, ConvertFormatsResponse
from app.utils.files import safe_path, get_user_storage_path

router = APIRouter()


@router.post("/audio", response_model=TaskResponse)
async def convert_audio(
    convert_data: ConvertAudio,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Convert audio file to different format"""
    user_storage = get_user_storage_path(current_user.username)
    input_path = safe_path(convert_data.input_path, str(user_storage))

    if not input_path.exists() or not input_path.is_file():
        raise HTTPException(status_code=404, detail="Input file not found")

    # Create task
    task_id = str(uuid.uuid4())
    task = TaskModel(
        id=task_id,
        user_id=current_user.id,
        type="convert_audio",
        status="pending",
        input_data={
            "input_path": convert_data.input_path,
            "output_format": convert_data.output_format,
            "quality": convert_data.quality
        }
    )
    db.add(task)
    db.commit()

    # TODO: Start background task for conversion using ffmpeg
    # For now, return task ID

    return TaskResponse(
        task_id=task_id,
        status="pending",
        progress=0
    )


@router.post("/image", response_model=TaskResponse)
async def convert_image(
    convert_data: ConvertImage,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Convert image to different format"""
    user_storage = get_user_storage_path(current_user.username)
    input_path = safe_path(convert_data.input_path, str(user_storage))

    if not input_path.exists() or not input_path.is_file():
        raise HTTPException(status_code=404, detail="Input file not found")

    # Create task
    task_id = str(uuid.uuid4())
    task = TaskModel(
        id=task_id,
        user_id=current_user.id,
        type="convert_image",
        status="pending",
        input_data={
            "input_path": convert_data.input_path,
            "output_format": convert_data.output_format,
            "quality": convert_data.quality
        }
    )
    db.add(task)
    db.commit()

    # TODO: Start background task for conversion using PIL/Pillow

    return TaskResponse(
        task_id=task_id,
        status="pending",
        progress=0
    )


@router.get("/status/{task_id}", response_model=TaskStatus)
async def get_task_status(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get conversion task status"""
    task = db.query(TaskModel).filter(
        TaskModel.id == task_id,
        TaskModel.user_id == current_user.id
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return TaskStatus(
        status=task.status,
        progress=task.progress,
        result=task.output_data,
        error=task.error
    )


@router.get("/formats", response_model=ConvertFormatsResponse)
async def get_supported_formats():
    """Get supported conversion formats"""
    return ConvertFormatsResponse(
        audio=["mp3", "wav", "flac", "ogg", "m4a", "aac"],
        image=["jpeg", "jpg", "png", "webp", "gif", "bmp"]
    )
