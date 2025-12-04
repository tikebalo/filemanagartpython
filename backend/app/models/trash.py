from sqlalchemy import Column, Integer, String, BigInteger, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from app.database import Base


class TrashItem(Base):
    __tablename__ = "trash"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    original_path = Column(String(500), nullable=False)
    trash_path = Column(String(500), nullable=False)
    size = Column(BigInteger, default=0)
    deleted_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(days=30))

    # Relationships
    user = relationship("User", back_populates="trash_items")
