from pathlib import Path
from typing import Optional, List
import magic
import mimetypes
from fastapi import HTTPException
from app.config import settings


def safe_path(user_path: str, base_dir: str) -> Path:
    """
    Ensure path is within base directory (prevent path traversal)
    """
    base = Path(base_dir).resolve()
    # Remove leading slashes and ensure relative path
    clean_path = user_path.lstrip('/')
    full_path = (base / clean_path).resolve()

    if not str(full_path).startswith(str(base)):
        raise HTTPException(status_code=403, detail="Access denied")

    return full_path


def get_user_storage_path(username: str) -> Path:
    """Get user's storage directory"""
    storage_path = Path(settings.STORAGE_PATH) / "users" / username
    storage_path.mkdir(parents=True, exist_ok=True)
    return storage_path


def get_trash_path(username: str) -> Path:
    """Get user's trash directory"""
    trash_path = Path(settings.STORAGE_PATH) / "trash" / username
    trash_path.mkdir(parents=True, exist_ok=True)
    return trash_path


def get_thumbnails_path() -> Path:
    """Get thumbnails directory"""
    thumbnails_path = Path(settings.STORAGE_PATH) / "thumbnails"
    thumbnails_path.mkdir(parents=True, exist_ok=True)
    return thumbnails_path


def get_file_mime_type(file_path: Path) -> str:
    """Get MIME type of a file"""
    try:
        mime = magic.Magic(mime=True)
        return mime.from_file(str(file_path))
    except:
        # Fallback to mimetypes
        mime_type, _ = mimetypes.guess_type(str(file_path))
        return mime_type or "application/octet-stream"


def get_file_category(mime_type: str) -> str:
    """Get file category from MIME type"""
    if mime_type.startswith("image/"):
        return "image"
    elif mime_type.startswith("video/"):
        return "video"
    elif mime_type.startswith("audio/"):
        return "audio"
    elif mime_type in ["application/pdf", "application/msword", "application/vnd.ms-excel",
                       "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                       "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                       "text/plain", "text/markdown"]:
        return "document"
    elif mime_type in ["application/zip", "application/x-tar", "application/gzip",
                       "application/x-rar", "application/x-7z-compressed"]:
        return "archive"
    else:
        return "other"


def format_size(size: int) -> str:
    """Format file size in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} PB"


def validate_filename(filename: str) -> bool:
    """Validate filename"""
    if not filename or filename in ['.', '..']:
        return False

    forbidden_chars = ['/', '\\', '\0', '<', '>', ':', '"', '|', '?', '*']
    if any(char in filename for char in forbidden_chars):
        return False

    # Check extension
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    if ext in settings.FORBIDDEN_EXTENSIONS:
        return False

    return True


def get_directory_size(path: Path) -> int:
    """Calculate total size of a directory"""
    total = 0
    try:
        for item in path.rglob('*'):
            if item.is_file():
                total += item.stat().st_size
    except Exception:
        pass
    return total


def find_unique_name(path: Path, name: str) -> str:
    """Find unique filename if file already exists"""
    if not (path / name).exists():
        return name

    base_name = name.rsplit('.', 1)[0] if '.' in name else name
    extension = '.' + name.rsplit('.', 1)[1] if '.' in name else ''

    counter = 1
    while (path / f"{base_name} ({counter}){extension}").exists():
        counter += 1

    return f"{base_name} ({counter}){extension}"
