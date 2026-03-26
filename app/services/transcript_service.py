import asyncio
from typing import Optional
from app.models.audit import TranscriptAudit
from app.services.cache_service import CacheService
from youtube_transcript_api import YouTubeTranscriptApi
from app.utils.transcript_utils import format_transcript, format_timestamp
from app.core.exceptions import (
    VideoUnavailableError,
    VideoPrivateError,
    LanguageNotSupportedError,
    TranscriptFetchError,
)
from app.core.logger import logger  # make sure this is imported
from sqlalchemy.orm import Session

async def get_transcript(
    db: Session, 
    video_id: str, 
    user_id: int,  # Now strictly required
    language: Optional[str] = None) -> dict:
    """
    Async transcript fetcher with Redis caching and detailed logging.
    """
    cache_key_lang = language or "default"
    logger.info(f"Transcript request received: video_id={video_id}, language={cache_key_lang}")

    # 1. Try cache first
    cached = await CacheService.get_transcript(video_id, cache_key_lang)
    if cached:
        logger.info(
            f"Cache HIT: transcript found for video_id={video_id}, language={cache_key_lang}"
        )
        # LOG AUDIT ON CACHE HIT
        _log_audit(db, video_id, user_id)
        return cached

    logger.info(
        f"Cache MISS: no cached transcript for video_id={video_id}, "
        f"language={cache_key_lang}. Fetching from YouTube API..."
    )

    loop = asyncio.get_event_loop()

    # 2. Run the blocking fetch in a thread executor
    def _fetch():
        ytt_api = YouTubeTranscriptApi()
        if language:
            return ytt_api.fetch(video_id, languages=[language])
        return ytt_api.fetch(video_id)

    try:
        transcript = await loop.run_in_executor(None, _fetch)
        logger.info(f"Fetched transcript from YouTube API for video_id={video_id}")
    except Exception as e:
        logger.error(f"Error fetching transcript from YouTube API for video_id={video_id}: {e}")
        if "VideoUnavailable" in str(e):
            raise VideoUnavailableError("Video unavailable or deleted")
        elif "TranscriptsDisabled" in str(e):
            raise VideoPrivateError("Transcript disabled or video private")
        elif "NoTranscriptFound" in str(e):
            raise LanguageNotSupportedError("Transcript not available in requested language")
        else:
            raise TranscriptFetchError(str(e))

    # 3. Build transcript with timestamps
    lines = []
    for idx, snippet in enumerate(transcript.snippets, start=1):
        start_time = format_timestamp(snippet.start)
        end_time = format_timestamp(snippet.start + snippet.duration)
        lines.append(f"{idx}\n{start_time} --> {end_time}\n{snippet.text}\n")

    data = format_transcript(transcript)

    result = {
        "video_id": video_id,
        "language": transcript.language,
        "language_code": transcript.language_code,
        "transcript": data,
        "transcript_with_timestamps": "\n".join(lines),
    }

    # 4. Save into cache (async, doesn’t block)
    await CacheService.set_transcript(video_id, cache_key_lang, result)
    
    # LOG AUDIT ON NEW FETCH
    _log_audit(db, video_id, user_id)
    
    logger.info(
        f"Transcript cached for video_id={video_id}, language={cache_key_lang}, "
        f"expiry=24h"
    )

    return result


def _log_audit(db: Session, video_id: str, user_id: int):
    """Helper to record activity for Admin Analytics."""
    try:
        new_audit = TranscriptAudit(video_id=video_id, user_id=user_id)
        db.add(new_audit)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Critical: Failed to log transcript audit for user {user_id}: {e}")