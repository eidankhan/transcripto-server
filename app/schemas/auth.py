from pydantic import BaseModel, EmailStr, Field
from enum import Enum
from datetime import datetime

# Define roles as an Enum for consistency across the app
class UserRole(str, Enum):
    ADMIN = "ADMIN"
    USER = "USER"

class SignUpRequest(BaseModel):
    name: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8)
    # Role is not included here to prevent users from 
    # sending "role": "ADMIN" in the POST body.

class VerifyEmailRequest(BaseModel):
    email: EmailStr
    code: str = Field(min_length=6, max_length=6, pattern=r"^\d{6}$")

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    name: str
    role: UserRole  # <--- This allows the Enum to be serialized correctly

    class Config:
        from_attributes = True

class PublicUser(BaseModel):
    id: int
    email: EmailStr
    is_verified: bool
    role: UserRole = UserRole.USER  # Default role for API visibility
    name: str        # <--- Added
    created_at: datetime # <--- Added
    
    class Config:
        from_attributes = True

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    email: str
    code: str
    new_password: str