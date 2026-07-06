"""
Model metadata and information endpoints.
"""

import logging
from fastapi import APIRouter, HTTPException

from models import ModelInfoResponse
from ml_engine import get_model, FEATURE_COLUMNS
from supabase_queries import get_model_metadata, get_feature_importance

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/metadata", response_model=ModelInfoResponse)
async def get_model_metadata_endpoint():
    """
    Get metadata about the currently active model.
    Returns training metrics, feature list, and confusion matrix.
    """
    metadata = get_model_metadata()
    
    if metadata:
        return ModelInfoResponse(
            model_version=metadata["model_version"],
            training_data_range=metadata.get("training_data_range", "Unknown"),
            roc_auc=float(metadata.get("roc_auc", 0)),
            accuracy=float(metadata.get("accuracy", 0)),
            precision=float(metadata.get("precision", 0)),
            recall=float(metadata.get("recall", 0)),
            total_features=metadata.get("total_features", len(FEATURE_COLUMNS)),
            feature_list=metadata.get("feature_list", FEATURE_COLUMNS),
            confusion_matrix=metadata.get("confusion_matrix", {}),
            is_active=metadata.get("is_active", True),
        )
    
    # Fallback: return actual training results (no database needed)
    return ModelInfoResponse(
        model_version="1.0",
        training_data_range="2018-2022",
        roc_auc=0.6720,
        accuracy=0.8241,
        precision=0.5900,
        recall=0.9900,
        total_features=9,
        feature_list=["Airline", "Origin", "Dest", "Distance", "Month", "DayofMonth", "DayOfWeek", "DepHour", "ArrHour"],
        confusion_matrix={"tn": 932298, "fp": 1391, "fn": 198212, "tp": 2002},
        is_active=True,
    )


@router.get("/feature-importance")
async def get_feature_importance_endpoint():
    """
    Get global feature importance scores for the active model.
    """
    # Try database first
    importance_records = get_feature_importance("1.0")
    
    if importance_records:
        return {
            "model_version": "1.0",
            "features": [
                {
                    "name": r["feature_name"],
                    "importance": float(r["importance_score"]),
                    "rank": r["rank"],
                }
                for r in importance_records
            ],
        }
    
    # Fallback: get from loaded model
    try:
        model = get_model()
        importance = model.get_feature_importance()
        
        # Sort by importance
        sorted_features = sorted(importance.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "model_version": "1.0",
            "features": [
                {
                    "name": name,
                    "importance": score,
                    "rank": rank + 1,
                }
                for rank, (name, score) in enumerate(sorted_features)
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Model not available: {e}")


@router.get("/airlines")
async def list_airlines():
    """List all available airlines."""
    from supabase_queries import get_all_airlines
    airlines = get_all_airlines()
    return {"airlines": airlines}


@router.get("/airports")
async def list_airports():
    """List all available airports."""
    from supabase_queries import get_all_airports
    airports = get_all_airports()
    return {"airports": airports}
