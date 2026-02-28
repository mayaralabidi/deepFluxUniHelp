"""User model for authentication and authorization."""

from datetime import datetime
from enum import Enum
from uuid import uuid4
from typing import Optional

from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from pydantic import BaseModel, EmailStr, Field

from backend.app.core.database import Base


class GUID(TypeDecorator):
    """Platform-independent GUID type. Uses UUID on PostgreSQL, CHAR(36) on SQLite."""
    impl = CHAR
    cache_ok = True
    
    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PG_UUID())
        return dialect.type_descriptor(CHAR(36))
    
    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if dialect.name == 'postgresql':
            return str(value)
        return str(value)
    
    def process_result_value(self, value, dialect):
        if value is None:
            return value
        return value


class UserRole(str, Enum):
    """User roles for RBAC."""
    STUDENT = "student"
    STAFF = "staff"
    ADMIN = "admin"


class User(Base):
    """SQLAlchemy User model."""
    __tablename__ = "users"
    
    id = Column(GUID(), primary_key=True, default=uuid4, nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    student_id = Column(String(50), nullable=True, unique=True, index=True)  # e.g., "STU123456"
    role = Column(SQLEnum(UserRole), default=UserRole.STUDENT, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self) -> str:
        return f"<User(email={self.email}, role={self.role})>"


# Pydantic schemas for API
class UserCreate(BaseModel):
    """Schema for user registration."""
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=1, max_length=255)
    student_id: Optional[str] = Field(None, max_length=50)


class UserRead(BaseModel):
    """Schema for user response (no password)."""
    id: str
    email: str
    full_name: str
    student_id: Optional[str]
    role: UserRole
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """Schema for login request."""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"
    user: UserRead


class TokenData(BaseModel):
    """Schema for decoded JWT token data."""
    user_id: str
    email: str
    role: UserRole
