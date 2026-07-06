"""
Health check endpoint for monitoring and load balancers.
"""

import os
import logging
from fastapi import APIRouter

from models import HealthResponse
from config import MODEL_VERSION

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        - status: "healthy" or "degraded"
        - model_loaded: Whether the ML model is loaded
        - database_connected: Whether Supabase is accessible
        - version: API version
    """
    # Check model
    model_loaded = False
    try:
        from ml_engine import get_model
        get_model()
        model_loaded = True
    except Exception as e:
        logger.warning(f"Health check - model not loaded: {e}")
    
    # Check database
    db_connected = False
    try:
        from database import db
        db_connected = db.is_connected()
    except Exception as e:
        logger.warning(f"Health check - database not connected: {e}")
    
    status = "healthy" if (model_loaded and db_connected) else "degraded"
    if not model_loaded:
        status = "unhealthy"
    
    return HealthResponse(
        status=status,
        model_loaded=model_loaded,
        database_connected=db_connected,
        version=MODEL_VERSION,
    )
