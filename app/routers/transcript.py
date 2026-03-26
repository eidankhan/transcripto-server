from typing import Optional
from fastapi import APIRouter, Query, Depends, status, Request
from fastapi.responses import JSONResponse  # ✅ Required for professional error handling
from sqlalchemy.orm import Session

from app.services.transcript_service import get_transcript
from app.services.limit_service import LimitService
from app.core.database import get_db
from app.core.exceptions import TranscriptError
from app.schemas.transcript import SuccessResponse, ErrorResponse
from app.core.logger import logger
from app.core.deps import get_optional_user

router = APIRouter(prefix="/v1/transcripts", tags=["transcripts"])

@router.get(
    "",
    response_model=SuccessResponse,
    responses={
        200: {"model": SuccessResponse, "description": "Transcript fetched successfully"},
        403: {"model": ErrorResponse, "description": "Daily limit reached or private video"},
        404: {"model": ErrorResponse, "description": "Video/Transcript unavailable"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Fetch transcript of a YouTube video",
    description="Returns cleaned transcript with guest rate limiting."
)
async def fetch_transcript(
    request: Request,
    video_id: str = Query(..., description="YouTube video ID"),
    language: Optional[str] = Query(None, description="Optional language code"),
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_optional_user)
):
    user_id = None
    
    if current_user:
        # Authenticated User Flow
        user_id = int(current_user['sub'])
        logger.info(f"Auth User {user_id} requested video_id={video_id}")
    else:
        # Anonymous Guest Flow (IP Rate Limited)
        client_ip = request.client.host
        logger.info(f"Guest IP {client_ip} requested video_id={video_id}")
        
        # Check if this IP has used up its 5 daily requests
        if not LimitService.check_anonymous_limit(db, client_ip):
            # ✅ PROFESSIONAL FIX: Return JSONResponse to bypass SuccessResponse validation
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "status": "error",
                    "code": 403,
                    "message": "Daily free limit reached. Please register to unlock more!",
                }
            )

    try:
        # Pass user_id (it will be None for guests)
        transcript = await get_transcript(
            db=db, 
            video_id=video_id, 
            user_id=user_id, 
            language=language
        )
        
        # This returns as SuccessResponse correctly
        return SuccessResponse(status="success", code=200, data=transcript)

    except TranscriptError as e:
        # ✅ ALSO FIX HERE: Use JSONResponse for caught service exceptions
        return JSONResponse(
            status_code=e.code,
            content={
                "status": "error", 
                "code": e.code, 
                "message": e.message
            }
        )
    except Exception as e:
        # Final safety net for 500 errors
        logger.error(f"Unhandled error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "code": 500,
                "message": "An internal server error occurred."
            }
        )