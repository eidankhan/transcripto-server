from typing import Optional
from fastapi import APIRouter, Query, Depends, status
from sqlalchemy.orm import Session

from app.services.transcript_service import get_transcript
from app.core.database import get_db  # Import your DB dependency
from app.core.exceptions import TranscriptError
from app.schemas.transcript import SuccessResponse, ErrorResponse
from app.core.logger import logger
from app.core.deps import get_current_user

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
    video_id: str = Query(..., description="YouTube video ID"),
    language: Optional[str] = Query(None, description="Optional language code"),
    db: Session = Depends(get_db),                # ✅ Inject DB Session
    current_user: dict = Depends(get_current_user) # ✅ Enforce JWT
):
    # Extract user_id from the 'sub' field (assuming 'sub' is the PK ID)
    user_id = int(current_user['sub'])
    
    logger.info(f"User {user_id} requested transcript for video_id={video_id}")

    try:
        # ✅ Pass DB and user_id to the service
        transcript = await get_transcript(
            db=db, 
            video_id=video_id, 
            user_id=user_id, 
            language=language
        )
        
        logger.info(f"Transcript fetched and audited for video_id={video_id}")

        # FastAPI handles the 200 OK and model serialization automatically
        return SuccessResponse(
            status="success",
            code=200,
            data=transcript,
        )

    except TranscriptError as e:
        logger.error(f"Error for video_id={video_id}: {e.message}")
        # Return the error schema directly; FastAPI handles the status_code via response_model
        return ErrorResponse(
            status="error",
            code=e.code,
            message=e.message,
            error=str(e),
        )