from fastapi import FastAPI
from app.core.database import Base, engine
from app.routers import auth as auth_router, transcript as transcript_router
from app.core.logger import logger
import logging   # <-- built-in Python logging



app = FastAPI(title="FastAPI User Auth Service")

# Create tables on startup
Base.metadata.create_all(bind=engine)

# Include auth routes
app.include_router(auth_router.router)
app.include_router(transcript_router.router)


@app.on_event("startup")
async def startup_event():
    logger.info("Application startup complete.")

@app.get("/ping")
async def ping():
    logger.info("Ping endpoint was called.")
    return {"message": "pong"}

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 Application shutting down, flushing logs...")
    logging.shutdown()