from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from datetime import datetime, timezone
from app.utils.security import decode_access_token
from app.core.redis import r  # your redis client

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Extract current user from JWT, also check if token is revoked.
    """
    try:
        payload = decode_access_token(token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # ✅ Revocation check
    token_key = f"revoked:{payload['sub']}:{payload['iat']}"
    is_revoked = await r.get(token_key)
    if is_revoked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload
