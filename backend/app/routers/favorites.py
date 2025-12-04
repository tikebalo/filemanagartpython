from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.favorite import Favorite
from app.schemas.file import FavoriteAdd, FileItem
from app.utils.files import safe_path, get_user_storage_path, get_file_mime_type, get_file_category
from datetime import datetime

router = APIRouter()


@router.get("/")
async def get_favorites(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's favorite files and folders"""
    favorites = db.query(Favorite).filter(Favorite.user_id == current_user.id).all()
    user_storage = get_user_storage_path(current_user.username)

    items = []
    for fav in favorites:
        try:
            file_path = safe_path(fav.path, str(user_storage))
            if not file_path.exists():
                # Remove from favorites if doesn't exist
                db.delete(fav)
                db.commit()
                continue

            stats = file_path.stat()

            if file_path.is_file():
                items.append(FileItem(
                    name=file_path.name,
                    type="file",
                    path=fav.path,
                    size=stats.st_size,
                    mime=get_file_mime_type(file_path),
                    modified=datetime.fromtimestamp(stats.st_mtime),
                    is_favorite=True
                ))
            elif file_path.is_dir():
                items.append(FileItem(
                    name=file_path.name,
                    type="folder",
                    path=fav.path,
                    modified=datetime.fromtimestamp(stats.st_mtime),
                    is_favorite=True,
                    items_count=len(list(file_path.iterdir()))
                ))
        except:
            continue

    return {"items": items}


@router.post("/")
async def add_favorite(
    favorite_data: FavoriteAdd,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add file or folder to favorites"""
    user_storage = get_user_storage_path(current_user.username)
    file_path = safe_path(favorite_data.path, str(user_storage))

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    # Check if already in favorites
    existing = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.path == favorite_data.path
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Already in favorites")

    favorite = Favorite(
        user_id=current_user.id,
        path=favorite_data.path
    )
    db.add(favorite)
    db.commit()

    return {"message": "Added to favorites"}


@router.delete("/")
async def remove_favorite(
    path: str = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove file or folder from favorites"""
    favorite = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.path == path
    ).first()

    if not favorite:
        raise HTTPException(status_code=404, detail="Not in favorites")

    db.delete(favorite)
    db.commit()

    return {"message": "Removed from favorites"}
