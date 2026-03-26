from sqlalchemy import Column, Integer, String, DateTime, func
from app.core.database import Base

class TranscriptAudit(Base):
    __tablename__ = "transcript_audits"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(String(50), nullable=False)
    user_id = Column(Integer, nullable=True) # Tracking which user, if logged in
    created_at = Column(DateTime(timezone=True), server_default=func.now())