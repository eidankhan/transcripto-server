from fastapi import FastAPI
from app.core.database import Base, engine
from app.routers import auth as auth_router, transcript as transcript_router
from app.core.logger import logger
import logging   # <-- built-in Python logging
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="FastAPI User Auth Service")

origins = [
    "http://localhost:3000",  # your Next.js dev URL
    "https://transcripto.dev", # your production frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # or ["*"] for all origins
    allow_credentials=True,
    allow_methods=["*"],            # <-- important: allows OPTIONS, POST, etc.
    allow_headers=["*"],            # <-- important: allows custom headers
)

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