from sqlalchemy import Column, String, Integer, Date, func
from app.core.database import Base

class AnonymousUsage(Base):
    __tablename__ = "anonymous_usage"

    ip_address = Column(String, primary_key=True, index=True)
    request_count = Column(Integer, default=0)
    last_request_date = Column(Date, default=func.current_date())