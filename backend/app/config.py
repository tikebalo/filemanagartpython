from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App
    APP_NAME: str = "FileManager Pro"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database
    DATABASE_URL: str = "sqlite:///./storage/database.db"

    # Storage
    STORAGE_PATH: str = "./storage"
    MAX_UPLOAD_SIZE: int = 5368709120  # 5 GB
    ALLOWED_EXTENSIONS: set = {
        'jpg', 'jpeg', 'png', 'gif', 'webp', 'svg', 'bmp', 'ico',
        'mp4', 'webm', 'ogg', 'mov', 'avi', 'mkv', 'flv', 'wmv',
        'mp3', 'wav', 'flac', 'ogg', 'm4a', 'aac', 'wma',
        'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'md', 'csv',
        'zip', 'tar', 'gz', 'rar', '7z', 'bz2',
        'json', 'xml', 'yml', 'yaml', 'ini', 'cfg', 'conf',
        'js', 'ts', 'jsx', 'tsx', 'py', 'java', 'c', 'cpp', 'h', 'hpp',
        'css', 'scss', 'sass', 'less', 'html', 'htm'
    }
    FORBIDDEN_EXTENSIONS: set = {'php', 'phtml', 'php3', 'php4', 'php5', 'phar', 'exe', 'sh', 'bat', 'cmd', 'com', 'scr'}

    # Quotas
    DEFAULT_USER_QUOTA: int = 5368709120  # 5 GB
    ADMIN_QUOTA: int = 0  # Unlimited

    # Trash
    TRASH_RETENTION_DAYS: int = 30

    # Share links
    SHARE_LINK_LENGTH: int = 10

    # CORS
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
