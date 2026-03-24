import enum

from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, UniqueConstraint, Enum as SqlEnum
from app.core.database import Base


class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    USER = "USER"
 
class User(Base):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("email", name="uq_users_email"),)

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, index=True, unique=True)
    password_hash = Column(String(255), nullable=False)
    is_verified = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # This line ensures the 'role' column is created in the DB via SQLAlchemy
    role = Column(SqlEnum(UserRole), default=UserRole.USER, nullable=False)