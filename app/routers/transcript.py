from typing import Optional
from app.services.limit_service import LimitService
from fastapi import APIRouter, Query, Depends, status, Request
from sqlalchemy.orm import Session

from app.services.transcript_service import get_transcript
from app.core.database import get_db  # Import your DB dependency
from app.core.exceptions import TranscriptError
from app.schemas.transcript import SuccessResponse, ErrorResponse
from app.core.logger import logger
from app.core.deps import get_current_user, get_optional_user

router = APIRouter(prefix="/v1/transcripts", tags=["transcripts"])

@router.get(
    "",
    response_model=SuccessResponse,
    responses={
        200: {"model": SuccessResponse, "description": "Transcript fetched successfully"},
        403: {"model": ErrorResponse, "description": "Video is private or transcript disabled"},
        404: {"model": ErrorResponse, "description": "Video unavailable"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Fetch transcript of a YouTube video",
    description="Returns cleaned transcript and audit-logged metadata."
)
async def fetch_transcript(
    request: Request, # <--- Added to get IP
    video_id: str = Query(..., description="YouTube video ID"),
    language: Optional[str] = Query(None, description="Optional language code"),
    db: Session = Depends(get_db),                # ✅ Inject DB Session
    # current_user: dict = Depends(get_current_user) # ✅ Enforce JWT
    current_user: Optional[dict] = Depends(get_optional_user) # <--- Made Optional
):
    user_id = None
    
    if current_user:
        # Authenticated User Flow (Unlimited or Subscription-based)
        user_id = int(current_user['sub'])
        logger.info(f"Auth User {user_id} requested video_id={video_id}")
    else:
        # Anonymous Guest Flow (IP Rate Limited)
        client_ip = request.client.host
        logger.info(f"Guest IP {client_ip} requested video_id={video_id}")
        
        # Check if this IP has used up its 5 daily requests
        if not LimitService.check_anonymous_limit(db, client_ip):
            return ErrorResponse(
                status="error",
                code=403,
                message="Daily free limit reached. Please register to unlock more!",
            )

    try:
        # Pass user_id (it will be None for guests)
        transcript = await get_transcript(
            db=db, 
            video_id=video_id, 
            user_id=user_id, 
            language=language
        )
        
        return SuccessResponse(status="success", code=200, data=transcript)

    except TranscriptError as e:
        return ErrorResponse(status="error", code=e.code, message=e.message)