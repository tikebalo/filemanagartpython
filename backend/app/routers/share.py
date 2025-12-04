from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from pathlib import Path

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.share_link import ShareLink
from app.schemas.share import ShareCreate, ShareResponse, SharePublicResponse, SharePasswordVerify
from app.utils.security import generate_share_id, hash_password, verify_password
from app.utils.files import safe_path, get_user_storage_path, get_file_mime_type
from app.config import settings

router = APIRouter()


@router.post("/", response_model=ShareResponse)
async def create_share_link(
    share_data: ShareCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create public share link"""
    user_storage = get_user_storage_path(current_user.username)
    file_path = safe_path(share_data.path, str(user_storage))

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    # Generate unique ID
    share_id = generate_share_id(settings.SHARE_LINK_LENGTH)
    while db.query(ShareLink).filter(ShareLink.id == share_id).first():
        share_id = generate_share_id(settings.SHARE_LINK_LENGTH)

    # Calculate expiration
    expires_at = None
    if share_data.expires_in:
        expires_at = datetime.utcnow() + timedelta(seconds=share_data.expires_in)

    # Hash password if provided
    password_hash = None
    if share_data.password:
        password_hash = hash_password(share_data.password)

    share_link = ShareLink(
        id=share_id,
        user_id=current_user.id,
        path=share_data.path,
        password_hash=password_hash,
        max_downloads=share_data.max_downloads,
        expires_at=expires_at
    )
    db.add(share_link)
    db.commit()

    return ShareResponse(
        id=share_id,
        path=share_data.path,
        url=f"/s/{share_id}",  # Frontend will prepend domain
        created_at=share_link.created_at,
        expires_at=expires_at,
        max_downloads=share_data.max_downloads,
        download_count=0,
        has_password=share_data.password is not None
    )


@router.get("/", response_model=List[ShareResponse])
async def get_user_share_links(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's share links"""
    share_links = db.query(ShareLink).filter(
        ShareLink.user_id == current_user.id
    ).order_by(ShareLink.created_at.desc()).all()

    return [
        ShareResponse(
            id=link.id,
            path=link.path,
            url=f"/s/{link.id}",
            created_at=link.created_at,
            expires_at=link.expires_at,
            max_downloads=link.max_downloads,
            download_count=link.download_count,
            has_password=link.password_hash is not None
        )
        for link in share_links
    ]


@router.delete("/{share_id}")
async def delete_share_link(
    share_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete share link"""
    share_link = db.query(ShareLink).filter(
        ShareLink.id == share_id,
        ShareLink.user_id == current_user.id
    ).first()

    if not share_link:
        raise HTTPException(status_code=404, detail="Share link not found")

    db.delete(share_link)
    db.commit()

    return {"message": "Share link deleted"}


@router.get("/public/{share_id}", response_model=SharePublicResponse)
async def get_public_share(
    share_id: str,
    password: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get public share content"""
    share_link = db.query(ShareLink).filter(ShareLink.id == share_id).first()

    if not share_link:
        raise HTTPException(status_code=404, detail="Share link not found")

    # Check expiration
    if share_link.expires_at and share_link.expires_at < datetime.utcnow():
        raise HTTPException(status_code=410, detail="Share link expired")

    # Check max downloads
    if share_link.max_downloads and share_link.download_count >= share_link.max_downloads:
        raise HTTPException(status_code=410, detail="Download limit reached")

    # Check password
    if share_link.password_hash:
        if not password:
            return SharePublicResponse(
                items=[],
                path=share_link.path,
                is_password_protected=True
            )
        if not verify_password(password, share_link.password_hash):
            raise HTTPException(status_code=403, detail="Incorrect password")

    # Get user and file
    user = db.query(User).filter(User.id == share_link.user_id).first()
    user_storage = get_user_storage_path(user.username)
    file_path = safe_path(share_link.path, str(user_storage))

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Shared file not found")

    items = []
    if file_path.is_file():
        stats = file_path.stat()
        items.append({
            "name": file_path.name,
            "type": "file",
            "size": stats.st_size,
            "mime": get_file_mime_type(file_path)
        })
    elif file_path.is_dir():
        for item in file_path.iterdir():
            stats = item.stat()
            if item.is_file():
                items.append({
                    "name": item.name,
                    "type": "file",
                    "size": stats.st_size,
                    "mime": get_file_mime_type(item)
                })
            elif item.is_dir():
                items.append({
                    "name": item.name,
                    "type": "folder",
                    "items_count": len(list(item.iterdir()))
                })

    return SharePublicResponse(
        items=items,
        path=share_link.path,
        is_password_protected=False
    )


@router.get("/public/{share_id}/download")
async def download_public_share(
    share_id: str,
    file: Optional[str] = Query(None),
    password: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Download from public share"""
    share_link = db.query(ShareLink).filter(ShareLink.id == share_id).first()

    if not share_link:
        raise HTTPException(status_code=404, detail="Share link not found")

    # Check expiration
    if share_link.expires_at and share_link.expires_at < datetime.utcnow():
        raise HTTPException(status_code=410, detail="Share link expired")

    # Check max downloads
    if share_link.max_downloads and share_link.download_count >= share_link.max_downloads:
        raise HTTPException(status_code=410, detail="Download limit reached")

    # Check password
    if share_link.password_hash:
        if not password or not verify_password(password, share_link.password_hash):
            raise HTTPException(status_code=403, detail="Incorrect password")

    # Get file
    user = db.query(User).filter(User.id == share_link.user_id).first()
    user_storage = get_user_storage_path(user.username)
    file_path = safe_path(share_link.path, str(user_storage))

    if file:
        # Download specific file from shared folder
        file_path = file_path / file

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    # Increment download count
    share_link.download_count += 1
    db.commit()

    from fastapi.responses import FileResponse
    return FileResponse(
        path=file_path,
        filename=file_path.name,
        media_type=get_file_mime_type(file_path)
    )
