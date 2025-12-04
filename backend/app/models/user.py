from sqlalchemy import Column, Integer, String, BigInteger, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
import enum


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), nullable=True)
    role = Column(SQLEnum(UserRole), default=UserRole.USER)
    quota = Column(BigInteger, default=5368709120)  # 5 GB
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # Settings
    theme = Column(String(20), default='system')
    language = Column(String(5), default='ru')
    accent_color = Column(String(20), default='blue')
    icon_size = Column(String(20), default='medium')

    # Relationships
    favorites = relationship("Favorite", back_populates="user", cascade="all, delete-orphan")
    activities = relationship("Activity", back_populates="user", cascade="all, delete-orphan")
    trash_items = relationship("TrashItem", back_populates="user", cascade="all, delete-orphan")
    share_links = relationship("ShareLink", back_populates="user", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")
