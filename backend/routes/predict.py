"""
Prediction endpoints: single flight prediction and airline comparison.
"""

import logging
from datetime import date, time
from fastapi import APIRouter, HTTPException

from models import (
    PredictionRequest, PredictionResponse, TopFactor,
    CompareAirlinesRequest, CompareAirlinesResponse, AirlineComparison,
)
from ml_engine import get_model, FEATURE_COLUMNS
from explainability import get_explainability_engine
from supabase_queries import (
    get_airline_id, get_route_data, get_all_airlines,
    save_prediction_record, save_explainability_factors,
)
from utils.validators import validate_airline, validate_airport, normalize_airline, KNOWN_AIRLINES
from utils.feature_engineering import build_features
from config import MODEL_VERSION

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/predict", response_model=PredictionResponse)
async def predict_flight(request: PredictionRequest):
    """
    Predict whether a flight will be delayed by 15+ minutes.
    
    Returns prediction with probability, confidence level, and
    top 3 explainability factors.
    """
    # Normalize airline name
    airline_name = normalize_airline(request.airline)
    if not airline_name:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown airline: '{request.airline}'. Use a valid US airline name."
        )
    
    # Validate airport codes
    origin = request.origin.upper()
    dest = request.dest.upper()
    if not validate_airport(origin):
        raise HTTPException(status_code=400, detail=f"Invalid origin airport code: '{origin}'")
    if not validate_airport(dest):
        raise HTTPException(status_code=400, detail=f"Invalid destination airport code: '{dest}'")
    if origin == dest:
        raise HTTPException(status_code=400, detail="Origin and destination must be different")
    
    try:
        # Build model features
        features = build_features(
            airline=airline_name,
            origin=origin,
            dest=dest,
            flight_date=request.flight_date,
            scheduled_dep_time=request.scheduled_dep_time,
            distance=request.distance,
        )
        
        # Run prediction
        model = get_model()
        predicted_delayed, delay_probability = model.predict(features)
        
        # Determine confidence level
        if delay_probability > 0.8 or delay_probability < 0.2:
            confidence = "high"
        elif 0.4 <= delay_probability <= 0.6:
            confidence = "moderate"
        else:
            confidence = "high"
        
        # Get explainability factors
        explainability = get_explainability_engine(model)
        top_factors = explainability.get_top_factors(features, top_n=3)
        
        # Get route historical stats
        route_data = get_route_data(origin, dest)
        route_delay_rate = route_data.get("historical_delay_rate") if route_data else None
        route_sample_count = route_data.get("sample_count") if route_data else None
        
        # Build response factors (strip 'label' key for response)
        response_factors = [
            TopFactor(
                feature=f["feature"],
                impact=f["impact"],
                direction=f["direction"],
            )
            for f in top_factors
        ]
        
        # Save prediction to database (non-blocking, best-effort)
        try:
            airline_id = get_airline_id(airline_name)
            route_id = route_data["id"] if route_data else None
            if airline_id and route_id:
                pred_id = save_prediction_record(
                    airline_id=airline_id,
                    route_id=route_id,
                    flight_date=str(request.flight_date),
                    scheduled_dep_time=str(request.scheduled_dep_time),
                    predicted_delayed=predicted_delayed,
                    delay_probability=delay_probability,
                    confidence=confidence,
                    model_version=MODEL_VERSION,
                )
                if pred_id:
                    save_explainability_factors(pred_id, top_factors)
        except Exception as e:
            logger.warning(f"Failed to save prediction to DB: {e}")
        
        return PredictionResponse(
            predicted_delayed=predicted_delayed,
            delay_probability=delay_probability,
            confidence=confidence,
            top_factors=response_factors,
            route_historical_delay_rate=route_delay_rate,
            route_sample_count=route_sample_count,
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prediction error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.post("/compare-airlines", response_model=CompareAirlinesResponse)
async def compare_airlines(request: CompareAirlinesRequest):
    """
    Compare predicted delay across multiple airlines for the same route.
    """
    origin = request.origin.upper()
    dest = request.dest.upper()
    
    if not validate_airport(origin) or not validate_airport(dest):
        raise HTTPException(status_code=400, detail="Invalid airport code")
    
    # Try database first, fall back to hardcoded list
    airlines = get_all_airlines()
    if not airlines:
        # Fallback: use the KNOWN_AIRLINES from validators
        airlines = [{"code": name, "name": name} for name in sorted(KNOWN_AIRLINES)]
    
    model = get_model()
    comparisons = []
    
    for airline_record in airlines[:5]:  # Limit to top 5 airlines
        airline_name = airline_record["name"]
        try:
            features = build_features(
                airline=airline_name,
                origin=origin,
                dest=dest,
                flight_date=request.flight_date,
                scheduled_dep_time=request.scheduled_dep_time,
            )
            
            predicted_delayed, delay_prob = model.predict(features)
            
            comparisons.append(AirlineComparison(
                airline=airline_record["code"],
                airline_name=airline_name,
                predicted_delayed=predicted_delayed,
                delay_probability=delay_prob,
            ))
        except Exception as e:
            logger.warning(f"Comparison failed for {airline_name}: {e}")
            continue
    
    # Sort by delay probability (lowest first = best airline for this route)
    comparisons.sort(key=lambda x: x.delay_probability)
    
    return CompareAirlinesResponse(
        route=f"{origin} → {dest}",
        comparisons=comparisons,
    )
