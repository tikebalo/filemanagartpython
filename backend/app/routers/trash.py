from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import shutil

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.trash import TrashItem as TrashItemModel
from app.schemas.file import TrashResponse, TrashItem, TrashRestore
from app.utils.files import get_trash_path, get_user_storage_path, safe_path

router = APIRouter()


@router.get("/", response_model=TrashResponse)
async def get_trash(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get items in trash"""
    trash_items = db.query(TrashItemModel).filter(
        TrashItemModel.user_id == current_user.id
    ).order_by(TrashItemModel.deleted_at.desc()).all()

    total_size = sum(item.size for item in trash_items)

    return TrashResponse(
        items=[TrashItem.from_orm(item) for item in trash_items],
        total_size=total_size
    )


@router.post("/restore")
async def restore_from_trash(
    restore_data: TrashRestore,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Restore items from trash"""
    user_storage = get_user_storage_path(current_user.username)
    trash_path = get_trash_path(current_user.username)

    restored = []
    errors = []

    for item_id in restore_data.ids:
        try:
            trash_item = db.query(TrashItemModel).filter(
                TrashItemModel.id == item_id,
                TrashItemModel.user_id == current_user.id
            ).first()

            if not trash_item:
                errors.append({"id": item_id, "error": "Not found in trash"})
                continue

            source = trash_path / trash_item.trash_path
            if not source.exists():
                # Clean up database
                db.delete(trash_item)
                db.commit()
                errors.append({"id": item_id, "error": "File not found in trash"})
                continue

            # Restore to original location
            destination = safe_path(trash_item.original_path, str(user_storage))

            # If original location exists, find unique name
            if destination.exists():
                from app.utils.files import find_unique_name
                unique_name = find_unique_name(destination.parent, destination.name)
                destination = destination.parent / unique_name

            # Ensure parent directory exists
            destination.parent.mkdir(parents=True, exist_ok=True)

            # Move back
            shutil.move(str(source), str(destination))

            # Remove from database
            db.delete(trash_item)
            db.commit()

            restored.append(item_id)

        except Exception as e:
            errors.append({"id": item_id, "error": str(e)})

    return {"restored": restored, "errors": errors}


@router.delete("/")
async def delete_from_trash(
    ids: List[int] = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Permanently delete items from trash"""
    trash_path = get_trash_path(current_user.username)

    deleted = []
    errors = []

    for item_id in ids:
        try:
            trash_item = db.query(TrashItemModel).filter(
                TrashItemModel.id == item_id,
                TrashItemModel.user_id == current_user.id
            ).first()

            if not trash_item:
                errors.append({"id": item_id, "error": "Not found"})
                continue

            source = trash_path / trash_item.trash_path
            if source.exists():
                if source.is_dir():
                    shutil.rmtree(str(source))
                else:
                    source.unlink()

            db.delete(trash_item)
            db.commit()

            deleted.append(item_id)

        except Exception as e:
            errors.append({"id": item_id, "error": str(e)})

    return {"deleted": deleted, "errors": errors}


@router.delete("/empty")
async def empty_trash(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Empty entire trash"""
    trash_path = get_trash_path(current_user.username)
    trash_items = db.query(TrashItemModel).filter(
        TrashItemModel.user_id == current_user.id
    ).all()

    deleted_count = 0
    for item in trash_items:
        try:
            source = trash_path / item.trash_path
            if source.exists():
                if source.is_dir():
                    shutil.rmtree(str(source))
                else:
                    source.unlink()

            db.delete(item)
            deleted_count += 1
        except:
            pass

    db.commit()

    return {"message": f"Emptied trash ({deleted_count} items deleted)"}


@router.post("/cleanup")
async def cleanup_expired(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Clean up expired trash items"""
    trash_path = get_trash_path(current_user.username)
    expired_items = db.query(TrashItemModel).filter(
        TrashItemModel.user_id == current_user.id,
        TrashItemModel.expires_at < datetime.utcnow()
    ).all()

    cleaned = 0
    for item in expired_items:
        try:
            source = trash_path / item.trash_path
            if source.exists():
                if source.is_dir():
                    shutil.rmtree(str(source))
                else:
                    source.unlink()

            db.delete(item)
            cleaned += 1
        except:
            pass

    db.commit()

    return {"message": f"Cleaned up {cleaned} expired items"}
