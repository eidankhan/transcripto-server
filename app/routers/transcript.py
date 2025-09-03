from typing import Optional
from fastapi import APIRouter, Query, Depends, status
from fastapi.responses import JSONResponse

from app.services.transcript_service import get_transcript
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
        422: {"model": ErrorResponse, "description": "Validation error"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Fetch transcript of a YouTube video",
    description="Returns cleaned transcript, raw data, and SRT-formatted timestamps."
)
async def fetch_transcript(
    video_id: str = Query(..., description="YouTube video ID, e.g., 'dQw4w9WgXcQ'"),
    language: Optional[str] = Query(None, description="Optional language code, e.g., 'en'"),
    current_user: dict = Depends(get_current_user)  # ✅ Enforce JWT here

):
    logger.info(f"User {current_user['sub']} requested transcript for video_id={video_id}, language={language}")

    try:
        # ✅ Directly await async get_transcript
        transcript = await get_transcript(video_id, language)
        logger.info(f"Transcript fetched successfully for video_id={video_id}")

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=SuccessResponse(
                status="success",
                code=200,
                data=transcript,
            ).dict(),
        )

    except TranscriptError as e:
        logger.error(f"Error fetching transcript for video_id={video_id}: {e}")
        return JSONResponse(
            status_code=e.code,
            content=ErrorResponse(
                status="error",
                code=e.code,
                message=e.message,
                error=str(e),
            ).dict(),
        )
