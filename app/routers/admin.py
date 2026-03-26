from fastapi import APIRouter, Depends, status
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.auth import PublicUser, UserRole
from app.core.deps import require_admin
from app.services.admin_service import AdminService

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/users", response_model=List[PublicUser])
async def get_all_users(
    db: Session = Depends(get_db), 
    admin=Depends(require_admin)
):
    """Fetch all users with the 'USER' role."""
    return AdminService.get_users_by_role(db, UserRole.USER)

@router.patch("/users/{user_id}", response_model=PublicUser)
async def update_user_status(
    user_id: int, 
    is_verified: bool, 
    db: Session = Depends(get_db), 
    admin=Depends(require_admin)
):
    """Manually verify or unverify a user."""
    return AdminService.update_user_verification(db, user_id, is_verified)

@router.delete("/users/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user(
    user_id: int, 
    db: Session = Depends(get_db), 
    admin=Depends(require_admin)
):
    """Permanently delete a user from the system."""
    AdminService.remove_user(db, user_id)
    return {"message": f"User {user_id} deleted successfully."}

@router.get("/stats", response_model=Dict[str, Any])
async def get_dashboard_stats(
    db: Session = Depends(get_db), 
    range: str = "monthly", # default to monthly
    admin=Depends(require_admin)
):
    """
    The heart of the Admin Dashboard.
    Returns Totals, Stickiness (DAU/MAU), and Usage Trends for Chart.js.
    """
    return AdminService.get_dashboard_stats(db, timeframe=range)