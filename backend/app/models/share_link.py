from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class ShareLink(Base):
    __tablename__ = "share_links"

    id = Column(String(20), primary_key=True)  # Short ID
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    path = Column(String(500), nullable=False)
    password_hash = Column(String(255), nullable=True)
    max_downloads = Column(Integer, nullable=True)
    download_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="share_links")
