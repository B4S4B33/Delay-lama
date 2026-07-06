"""
Supabase query helper functions.
Convenience wrappers around the Database class for common operations.
"""

import logging
from typing import Optional, List, Dict
from database import db

logger = logging.getLogger(__name__)


def get_airline_id(airline_name: str) -> Optional[int]:
    """
    Fetch airline ID by name.
    
    Args:
        airline_name: Full airline name (e.g., "United Airlines")
        
    Returns:
        Airline ID or None if not found
    """
    record = db.get_airline_by_code(airline_name)
    return record["id"] if record else None


def get_airport_id(airport_code: str) -> Optional[int]:
    """
    Fetch airport ID by 3-letter code.
    
    Args:
        airport_code: 3-letter IATA code (e.g., "ORD")
        
    Returns:
        Airport ID or None if not found
    """
    record = db.get_airport_by_code(airport_code.upper())
    return record["id"] if record else record


def get_route_data(origin_code: str, dest_code: str) -> Optional[Dict]:
    """
    Fetch route with historical statistics.
    
    Args:
        origin_code: Origin airport code
        dest_code: Destination airport code
        
    Returns:
        Dict with route stats or None
    """
    return db.get_route(origin_code.upper(), dest_code.upper())


def get_all_airlines() -> List[Dict]:
    """
    Fetch all airlines from the database.
    
    Returns:
        List of dicts with 'code' and 'name' keys
    """
    return db.get_all_airlines()


def get_all_airports() -> List[Dict]:
    """
    Fetch all airports from the database.
    
    Returns:
        List of dicts with 'code', 'name', 'city', 'state' keys
    """
    return db.get_all_airports()


def save_prediction_record(
    airline_id: int,
    route_id: int,
    flight_date: str,
    scheduled_dep_time: str,
    predicted_delayed: bool,
    delay_probability: float,
    confidence: str,
    model_version: str = "1.0",
    user_id: Optional[str] = None,
) -> Optional[str]:
    """
    Save a prediction to the database.
    
    Returns:
        Prediction UUID or None on failure
    """
    data = {
        "airline_id": airline_id,
        "route_id": route_id,
        "flight_date": flight_date,
        "scheduled_dep_time": scheduled_dep_time,
        "predicted_delayed": predicted_delayed,
        "delay_probability": delay_probability,
        "confidence": confidence,
        "model_version": model_version,
    }
    if user_id:
        data["user_id"] = user_id
    
    return db.save_prediction(data)


def save_explainability_factors(prediction_id: str, factors: List[Dict]) -> bool:
    """
    Save explainability factors for a prediction.
    
    Args:
        prediction_id: UUID of the prediction
        factors: List of factor dicts from ExplainabilityEngine
        
    Returns:
        True if all factors saved successfully
    """
    return db.save_explainability_factors(prediction_id, factors)


def save_batch_upload(file_name: str, file_path: str = "") -> Optional[str]:
    """
    Create a batch upload record.
    
    Returns:
        Batch UUID or None on failure
    """
    return db.save_batch_upload({
        "file_name": file_name,
        "file_path": file_path,
        "status": "pending"
    })


def update_batch_status(batch_id: str, **kwargs) -> bool:
    """
    Update batch upload status.
    
    Args:
        batch_id: UUID of the batch upload
        **kwargs: Fields to update (status, total_rows, processed_rows, etc.)
    """
    return db.update_batch_upload(batch_id, kwargs)


def get_batch_status(batch_id: str) -> Optional[Dict]:
    """
    Get batch upload status.
    
    Returns:
        Batch record dict or None
    """
    return db.get_batch_upload(batch_id)


def get_model_metadata() -> Optional[Dict]:
    """
    Fetch active model metadata.
    
    Returns:
        Model metadata dict or None
    """
    return db.get_active_model_metadata()


def get_feature_importance(model_version: str = "1.0") -> List[Dict]:
    """
    Fetch feature importance for a model version.
    
    Returns:
        List of feature importance records
    """
    return db.get_feature_importance(model_version)
