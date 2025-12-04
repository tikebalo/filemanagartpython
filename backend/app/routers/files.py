from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, Response
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from pathlib import Path
import shutil
import aiofiles
from datetime import datetime

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.favorite import Favorite
from app.models.trash import TrashItem
from app.schemas.file import (
    FileListResponse, FileItem, FileUploadResponse,
    FileRename, FileMove, FileCopy, FileSearch
)
from app.utils.files import (
    safe_path, get_user_storage_path, get_file_mime_type,
    get_file_category, validate_filename, get_directory_size,
    find_unique_name, get_trash_path
)
from app.utils.validators import validate_file_size, validate_file_extension

router = APIRouter()


@router.get("/", response_model=FileListResponse)
async def list_files(
    path: str = Query("/"),
    sort: str = Query("name", pattern="^(name|size|date)$"),
    order: str = Query("asc", pattern="^(asc|desc)$"),
    filter_type: Optional[str] = Query(None, alias="filter"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List files and folders"""
    user_storage = get_user_storage_path(current_user.username)
    target_path = safe_path(path, str(user_storage))

    if not target_path.exists():
        raise HTTPException(status_code=404, detail="Path not found")

    if not target_path.is_dir():
        raise HTTPException(status_code=400, detail="Path is not a directory")

    # Get favorites for this user
    favorites = {f.path for f in db.query(Favorite).filter(Favorite.user_id == current_user.id).all()}

    items = []
    total_size = 0

    for item in target_path.iterdir():
        try:
            stats = item.stat()
            relative_path = f"{path.rstrip('/')}/{item.name}"

            if item.is_file():
                mime_type = get_file_mime_type(item)
                category = get_file_category(mime_type)

                # Apply filter
                if filter_type and category != filter_type and filter_type != "all":
                    continue

                file_item = FileItem(
                    name=item.name,
                    type="file",
                    path=relative_path,
                    size=stats.st_size,
                    mime=mime_type,
                    modified=datetime.fromtimestamp(stats.st_mtime),
                    is_favorite=relative_path in favorites
                )
                items.append(file_item)
                total_size += stats.st_size

            elif item.is_dir():
                # Count items in folder
                items_count = len(list(item.iterdir()))
                folder_size = get_directory_size(item)

                folder_item = FileItem(
                    name=item.name,
                    type="folder",
                    path=relative_path,
                    modified=datetime.fromtimestamp(stats.st_mtime),
                    is_favorite=relative_path in favorites,
                    items_count=items_count,
                    size=folder_size
                )
                items.append(folder_item)
                total_size += folder_size

        except Exception as e:
            continue

    # Sort items
    if sort == "name":
        items.sort(key=lambda x: x.name.lower(), reverse=(order == "desc"))
    elif sort == "size":
        items.sort(key=lambda x: x.size or 0, reverse=(order == "desc"))
    elif sort == "date":
        items.sort(key=lambda x: x.modified, reverse=(order == "desc"))

    # Folders first
    items.sort(key=lambda x: x.type != "folder")

    # Get parent path
    parent = str(Path(path).parent) if path != "/" else None

    return FileListResponse(
        items=items,
        path=path,
        parent=parent,
        total_size=total_size
    )


@router.post("/upload", response_model=FileUploadResponse)
async def upload_files(
    files: List[UploadFile] = File(...),
    path: str = Query("/"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload files"""
    user_storage = get_user_storage_path(current_user.username)
    target_path = safe_path(path, str(user_storage))

    if not target_path.exists():
        target_path.mkdir(parents=True, exist_ok=True)

    uploaded = []
    errors = []

    # Calculate current used space
    used_space = get_directory_size(user_storage)

    for file in files:
        try:
            # Validate filename
            if not validate_filename(file.filename):
                errors.append({"file": file.filename, "error": "Invalid filename"})
                continue

            # Validate extension
            is_valid, error = validate_file_extension(file.filename)
            if not is_valid:
                errors.append({"file": file.filename, "error": error})
                continue

            # Read file size
            content = await file.read()
            file_size = len(content)

            # Validate quota
            is_valid, error = validate_file_size(file_size, current_user.quota, used_space)
            if not is_valid:
                errors.append({"file": file.filename, "error": error})
                continue

            # Find unique name if file exists
            unique_name = find_unique_name(target_path, file.filename)
            file_path = target_path / unique_name

            # Write file
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(content)

            uploaded.append(unique_name)
            used_space += file_size

        except Exception as e:
            errors.append({"file": file.filename, "error": str(e)})

    return FileUploadResponse(uploaded=uploaded, errors=errors)


@router.get("/download")
async def download_file(
    path: str = Query(...),
    current_user: User = Depends(get_current_user)
):
    """Download file"""
    user_storage = get_user_storage_path(current_user.username)
    file_path = safe_path(path, str(user_storage))

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    if not file_path.is_file():
        raise HTTPException(status_code=400, detail="Path is not a file")

    # Return file with support for range requests
    return FileResponse(
        path=file_path,
        filename=file_path.name,
        media_type=get_file_mime_type(file_path)
    )


@router.delete("/")
async def delete_files(
    paths: List[str] = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete files (move to trash)"""
    user_storage = get_user_storage_path(current_user.username)
    trash_path = get_trash_path(current_user.username)

    deleted = []
    errors = []

    for path in paths:
        try:
            source = safe_path(path, str(user_storage))
            if not source.exists():
                errors.append({"path": path, "error": "Not found"})
                continue

            # Generate unique trash name
            trash_name = f"{source.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            destination = trash_path / trash_name

            # Move to trash
            shutil.move(str(source), str(destination))

            # Record in database
            size = get_directory_size(destination) if destination.is_dir() else destination.stat().st_size
            trash_item = TrashItem(
                user_id=current_user.id,
                original_path=path,
                trash_path=trash_name,
                size=size
            )
            db.add(trash_item)
            db.commit()

            deleted.append(path)

        except Exception as e:
            errors.append({"path": path, "error": str(e)})

    return {"deleted": deleted, "errors": errors}


@router.put("/rename")
async def rename_file(
    rename_data: FileRename,
    current_user: User = Depends(get_current_user)
):
    """Rename file or folder"""
    user_storage = get_user_storage_path(current_user.username)
    source = safe_path(rename_data.path, str(user_storage))

    if not source.exists():
        raise HTTPException(status_code=404, detail="File not found")

    if not validate_filename(rename_data.new_name):
        raise HTTPException(status_code=400, detail="Invalid filename")

    destination = source.parent / rename_data.new_name

    if destination.exists():
        raise HTTPException(status_code=400, detail="File already exists")

    source.rename(destination)

    return {"message": "Renamed successfully"}


@router.put("/move")
async def move_files(
    move_data: FileMove,
    current_user: User = Depends(get_current_user)
):
    """Move files or folders"""
    user_storage = get_user_storage_path(current_user.username)
    dest_path = safe_path(move_data.destination, str(user_storage))

    if not dest_path.exists():
        dest_path.mkdir(parents=True, exist_ok=True)

    moved = []
    errors = []

    for path in move_data.paths:
        try:
            source = safe_path(path, str(user_storage))
            if not source.exists():
                errors.append({"path": path, "error": "Not found"})
                continue

            destination = dest_path / source.name
            if destination.exists():
                # Find unique name
                unique_name = find_unique_name(dest_path, source.name)
                destination = dest_path / unique_name

            shutil.move(str(source), str(destination))
            moved.append(path)

        except Exception as e:
            errors.append({"path": path, "error": str(e)})

    return {"moved": moved, "errors": errors}


@router.put("/copy")
async def copy_files(
    copy_data: FileCopy,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Copy files or folders"""
    user_storage = get_user_storage_path(current_user.username)
    dest_path = safe_path(copy_data.destination, str(user_storage))

    if not dest_path.exists():
        dest_path.mkdir(parents=True, exist_ok=True)

    copied = []
    errors = []
    total_size = 0

    for path in copy_data.paths:
        try:
            source = safe_path(path, str(user_storage))
            if not source.exists():
                errors.append({"path": path, "error": "Not found"})
                continue

            # Calculate size
            size = get_directory_size(source) if source.is_dir() else source.stat().st_size
            total_size += size

            # Check quota
            used_space = get_directory_size(user_storage)
            is_valid, error = validate_file_size(size, current_user.quota, used_space)
            if not is_valid:
                errors.append({"path": path, "error": error})
                continue

            destination = dest_path / source.name
            if destination.exists():
                unique_name = find_unique_name(dest_path, source.name)
                destination = dest_path / unique_name

            if source.is_dir():
                shutil.copytree(str(source), str(destination))
            else:
                shutil.copy2(str(source), str(destination))

            copied.append(path)

        except Exception as e:
            errors.append({"path": path, "error": str(e)})

    return {"copied": copied, "errors": errors}


@router.post("/search")
async def search_files(
    search_data: FileSearch,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search files by name"""
    user_storage = get_user_storage_path(current_user.username)
    search_path = safe_path(search_data.path, str(user_storage))

    if not search_path.exists():
        raise HTTPException(status_code=404, detail="Path not found")

    query = search_data.query.lower()
    results = []

    # Get favorites
    favorites = {f.path for f in db.query(Favorite).filter(Favorite.user_id == current_user.id).all()}

    def search_recursive(path: Path, base_path: str):
        try:
            for item in path.iterdir():
                if query in item.name.lower():
                    stats = item.stat()
                    relative_path = f"{base_path}/{item.name}".replace("//", "/")

                    if item.is_file():
                        results.append(FileItem(
                            name=item.name,
                            type="file",
                            path=relative_path,
                            size=stats.st_size,
                            mime=get_file_mime_type(item),
                            modified=datetime.fromtimestamp(stats.st_mtime),
                            is_favorite=relative_path in favorites
                        ))
                    elif item.is_dir():
                        results.append(FileItem(
                            name=item.name,
                            type="folder",
                            path=relative_path,
                            modified=datetime.fromtimestamp(stats.st_mtime),
                            is_favorite=relative_path in favorites,
                            items_count=len(list(item.iterdir()))
                        ))

                if search_data.recursive and item.is_dir():
                    search_recursive(item, relative_path)
        except:
            pass

    search_recursive(search_path, search_data.path)

    return {"results": results}
