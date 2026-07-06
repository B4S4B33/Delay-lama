"""
US Flight Delay Predictor — FastAPI Backend
Main application entry point with CORS, route registration, and startup events.
"""

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if os.getenv("DEBUG", "False").lower() == "true" else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# CORS origins
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    logger.info("🚀 Starting US Flight Delay Predictor API...")
    
    # Validate environment variables
    required_vars = ["SUPABASE_URL", "SUPABASE_KEY", "SUPABASE_SERVICE_KEY"]
    missing = [v for v in required_vars if not os.getenv(v)]
    if missing:
        logger.warning(f"⚠️  Missing env vars: {missing}. Running in demo mode.")
    
    # Load ML model
    try:
        from ml_engine import get_model
        _model = get_model()
        logger.info(f"✅ ML Model loaded: {_model.model_path}")
    except Exception as e:
        logger.error(f"❌ Failed to load ML model: {e}")
    
    yield
    
    logger.info("👋 Shutting down API...")


app = FastAPI(
    title="US Flight Delay Predictor",
    description="ML-powered flight delay prediction with explainability, airline comparison, and batch processing.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register route modules
from routes.predict import router as predict_router
from routes.batch import router as batch_router
from routes.metadata import router as metadata_router
from routes.health import router as health_router

app.include_router(predict_router, tags=["Predictions"])
app.include_router(batch_router, tags=["Batch Processing"])
app.include_router(metadata_router, tags=["Model Metadata"])
app.include_router(health_router, tags=["Health"])


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API info."""
    return {
        "name": "US Flight Delay Predictor",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=os.getenv("DEBUG", "False").lower() == "true",
    )
