from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.models.user import User
from app.core.database import get_db
from app.schemas.auth import PublicUser, UserRole
from app.core.deps import require_admin



router = APIRouter(prefix="/admin", tags=["Admin"])

# 1. READ: Get all users with the role 'USER'
@router.get("/users", response_model=List[PublicUser])
async def get_all_users(
    db=Depends(get_db), 
    admin=Depends(require_admin)
):
    users = db.query(User).filter(User.role == UserRole.USER).all()
    return users

# 2. UPDATE: Manually verify a user or change their name
@router.patch("/users/{user_id}", response_model=PublicUser)
async def update_user_status(
    user_id: int, 
    is_verified: bool, 
    db=Depends(get_db), 
    admin=Depends(require_admin)
):
    user = db.query(User).filter(User.id == user_id, User.role == UserRole.USER).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_verified = is_verified
    db.commit()
    db.refresh(user)
    return user

# 3. DELETE: Remove a user from the system
@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int, 
    db=Depends(get_db), 
    admin=Depends(require_admin)
):
    user = db.query(User).filter(User.id == user_id, User.role == UserRole.USER).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    return {"message": f"User {user_id} has been deleted successfully."}