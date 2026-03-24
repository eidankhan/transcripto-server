import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import Base, engine
from app.routers import auth as auth_router, transcript as transcript_router, admin
from app.core.logger import logger
from app.utils.create_admin import create_initial_admin  # Ensure this file is in your root
from app.core.logger import logger, log_requests_middleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup Logic ---
    logger.info("🚀 Application starting up...")
    
    # 1. Automatically create tables (replaces your standalone metadata line)
    # Using 'begin' ensures the schema is committed before moving to admin creation
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Database tables verified/created.")

    # 2. Run your Admin Automation
    try:
        await create_initial_admin()
        logger.info("👤 Admin check/creation complete.")
    except Exception as e:
        logger.error(f"❌ Failed to ensure admin user: {e}")

    yield 
    
    # --- Shutdown Logic ---
    logger.info("🛑 Application shutting down, flushing logs...")
    logging.shutdown()

# Initialize FastAPI with the lifespan manager
app = FastAPI(title="FastAPI User Auth Service", lifespan=lifespan)


# Register the Middleware
@app.middleware("http")
async def request_logging_context(request: Request, call_next):
    return await log_requests_middleware(request, call_next)

# CORS Configuration
origins = [
    "http://localhost:3000",
    "https://transcripto.dev",
    "https://www.transcripto.dev"
    "https://api.transcripto.dev",
    "https://www.api.transcripto.dev"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(auth_router.router)
app.include_router(transcript_router.router)
app.include_router(admin.router) # Now protected by your admin dependency

@app.get("/ping")
async def ping():
    logger.info("Ping endpoint was called.")
    return {"message": "pong"}