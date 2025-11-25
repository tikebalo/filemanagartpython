import re
from typing import Optional
from app.config import settings


def validate_username(username: str) -> tuple[bool, Optional[str]]:
    """Validate username"""
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    if len(username) > 50:
        return False, "Username must not exceed 50 characters"
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        return False, "Username can only contain letters, numbers, underscores and hyphens"
    return True, None


def validate_password(password: str) -> tuple[bool, Optional[str]]:
    """Validate password strength"""
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    return True, None


def validate_file_size(size: int, quota: int, used_space: int) -> tuple[bool, Optional[str]]:
    """Validate if file size is within quota"""
    if quota > 0:  # 0 means unlimited (admin)
        if used_space + size > quota:
            return False, "File size exceeds available quota"
    return True, None


def validate_file_extension(filename: str) -> tuple[bool, Optional[str]]:
    """Validate file extension"""
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''

    if ext in settings.FORBIDDEN_EXTENSIONS:
        return False, f"File type '{ext}' is not allowed"

    return True, None


def validate_path(path: str) -> tuple[bool, Optional[str]]:
    """Validate path format"""
    if not path.startswith('/'):
        return False, "Path must start with /"

    # Check for path traversal attempts
    if '..' in path or path.count('//') > 0:
        return False, "Invalid path"

    return True, None
