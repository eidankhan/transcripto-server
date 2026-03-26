import os
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import jwt, JWTError
from app.core.config import JWT_SECRET, JWT_ALG, ACCESS_TOKEN_EXPIRE_MINUTES
from fastapi import HTTPException, status

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

def create_access_token(sub: str, role: str) -> str:
    """
    Generates a JWT with user ID (sub) and permissions (role).
    """
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    payload = {
        "sub": str(sub), # Ensure sub is a string for JWT standards
        "role": role, 
        "iat": int(now.timestamp()), 
        "exp": int(expire.timestamp())
    }
    
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)

def decode_access_token(token: str) -> dict:
    """
    Decode a JWT and return the payload.
    Raises HTTPException if invalid or expired.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
def refresh_access_token(refresh_token: str) -> dict:
    """
    Creates a new access token from a valid refresh token.
    Note: Requires 'role' to be present in the refresh token payload.
    """
    try:
        payload = jwt.decode(refresh_token, JWT_SECRET, algorithms=[JWT_ALG])
        sub = payload.get("sub")
        role = payload.get("role")

        if not sub or not role:
            raise JWTError("Missing payload claims")

        # Generate new access token with the same identity and role
        new_access = create_access_token(sub=sub, role=role)

        return {"access_token": new_access, "token_type": "bearer"}

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )