from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pathlib import Path

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.file import FolderCreate
from app.utils.files import safe_path, get_user_storage_path, validate_filename

router = APIRouter()


@router.post("/")
async def create_folder(
    folder_data: FolderCreate,
    current_user: User = Depends(get_current_user)
):
    """Create new folder"""
    user_storage = get_user_storage_path(current_user.username)
    parent_path = safe_path(folder_data.path, str(user_storage))

    if not parent_path.exists():
        raise HTTPException(status_code=404, detail="Parent path not found")

    if not parent_path.is_dir():
        raise HTTPException(status_code=400, detail="Parent path is not a directory")

    if not validate_filename(folder_data.name):
        raise HTTPException(status_code=400, detail="Invalid folder name")

    folder_path = parent_path / folder_data.name

    if folder_path.exists():
        raise HTTPException(status_code=400, detail="Folder already exists")

    folder_path.mkdir(parents=True, exist_ok=False)

    return {"message": "Folder created successfully", "path": f"{folder_data.path}/{folder_data.name}"}


@router.delete("/")
async def delete_folder(
    path: str,
    current_user: User = Depends(get_current_user)
):
    """Delete empty folder"""
    user_storage = get_user_storage_path(current_user.username)
    folder_path = safe_path(path, str(user_storage))

    if not folder_path.exists():
        raise HTTPException(status_code=404, detail="Folder not found")

    if not folder_path.is_dir():
        raise HTTPException(status_code=400, detail="Path is not a folder")

    # Check if folder is empty
    if list(folder_path.iterdir()):
        raise HTTPException(status_code=400, detail="Folder is not empty")

    folder_path.rmdir()

    return {"message": "Folder deleted successfully"}


@router.get("/tree")
async def get_folder_tree(
    current_user: User = Depends(get_current_user)
):
    """Get folder tree for navigation"""
    user_storage = get_user_storage_path(current_user.username)

    def build_tree(path: Path, relative_path: str = "/"):
        """Recursively build folder tree"""
        tree = {
            "name": path.name or "Root",
            "path": relative_path,
            "children": []
        }

        try:
            for item in sorted(path.iterdir(), key=lambda x: x.name.lower()):
                if item.is_dir():
                    child_path = f"{relative_path}/{item.name}".replace("//", "/")
                    tree["children"].append(build_tree(item, child_path))
        except PermissionError:
            pass

        return tree

    tree = build_tree(user_storage)
    return tree
