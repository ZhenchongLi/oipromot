"""
Main FastAPI application for OiPromot.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from .core.config import get_settings
from .core.logging import setup_logging
from .routes.prompts import router as prompts_router

# Set up logging
logger = setup_logging()

# Get settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="OiPromot API",
    description="OfficeAI User End Prompt Project API",
    version="0.1.0",
    default_response_class=ORJSONResponse,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(prompts_router, prefix="/api/v1/prompts", tags=["prompts"])


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    logger.debug("Health check requested")
    return {"status": "healthy", "version": "0.1.0"}


@app.on_event("startup")
async def startup_event():
    """Application startup event."""
    logger.info("OiPromot API starting up")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event."""
    logger.info("OiPromot API shutting down")