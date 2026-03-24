import os
import logging
import sys
import time
import uuid
from logging.handlers import RotatingFileHandler
from fastapi import Request

# ---------------------------
# Path & Directory Setup
# ---------------------------
# Navigates to the project root where 'logs/' should live
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
logs_dir = os.path.join(project_root, "logs")
os.makedirs(logs_dir, exist_ok=True)

log_file_path = os.path.join(logs_dir, "api.log")

# ---------------------------
# Logging Configuration
# ---------------------------
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# Detailed format: Timestamp | Level | Module:Line | Message
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(module)s:%(lineno)d | %(message)s"
)

# 1. Console Handler (for Docker logs / stdout)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)

# 2. Rotating File Handler (5MB limit per file, keeping 5 backups)
file_handler = RotatingFileHandler(
    log_file_path, maxBytes=5*1024*1024, backupCount=5, encoding="utf-8"
)
file_handler.setFormatter(formatter)

# ---------------------------
# Logger Initialization
# ---------------------------
def setup_logging():
    # Root logger setup to intercept library logs (uvicorn, sqlalchemy, etc.)
    root_logger = logging.getLogger()
    root_logger.setLevel(LOG_LEVEL)
    
    if not root_logger.hasHandlers():
        root_logger.addHandler(console_handler)
        root_logger.addHandler(file_handler)

    # Specific app logger
    app_logger = logging.getLogger("transcripto")
    app_logger.info(f"🚀 Logger initialized. Level: {LOG_LEVEL} | File: {log_file_path}")
    return app_logger

logger = setup_logging()

# ---------------------------
# Middleware Function
# ---------------------------
async def log_requests_middleware(request: Request, call_next):
    """
    Logs every incoming HTTP request, its execution time, and status code.
    """
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    # Log the incoming call
    logger.info(f"ID: {request_id} | Req: {request.method} {request.url.path}")

    try:
        response = await call_next(request)
        
        # Calculate processing time in milliseconds
        process_time = (time.time() - start_time) * 1000
        formatted_time = f"{process_time:.2f}ms"

        # Log completion
        logger.info(
            f"ID: {request_id} | Res: {response.status_code} | Time: {formatted_time}"
        )

        # Inject Request ID into headers for frontend debugging
        response.headers["X-Request-ID"] = request_id
        return response

    except Exception as e:
        # Log unhandled exceptions that occur during the request
        process_time = (time.time() - start_time) * 1000
        logger.error(f"ID: {request_id} | Failed: {str(e)} | Time: {process_time:.2f}ms")
        raise e