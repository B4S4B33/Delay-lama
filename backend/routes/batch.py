"""
Batch prediction endpoints for CSV and Excel file uploads.
"""

import io
import json
import logging
import pandas as pd
from fastapi import APIRouter, UploadFile, File, HTTPException

from models import BatchUploadResponse, BatchStatusResponse
from ml_engine import get_model, FEATURE_COLUMNS, CATEGORICAL_COLUMNS
from explainability import get_explainability_engine
from utils.feature_engineering import build_features_from_csv_row
from supabase_queries import save_batch_upload, update_batch_status, get_batch_status
from config import MODEL_VERSION

logger = logging.getLogger(__name__)
router = APIRouter()

MAX_FILE_SIZE_MB = 10
ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls"}


def _read_uploaded_file(contents: bytes, filename: str) -> pd.DataFrame:
    """
    Read a CSV or Excel file into a DataFrame.
    
    Args:
        contents: Raw file bytes
        filename: Original filename (used to determine format)
        
    Returns:
        Parsed DataFrame
    """
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    
    if ext == ".csv":
        return pd.read_csv(io.BytesIO(contents))
    elif ext in (".xlsx", ".xls"):
        return pd.read_excel(io.BytesIO(contents), engine="openpyxl" if ext == ".xlsx" else "xlrd")
    else:
        raise ValueError(f"Unsupported file format: {ext}")


@router.post("/predict-batch", response_model=BatchUploadResponse)
async def predict_batch(file: UploadFile = File(...)):
    """
    Process a CSV or Excel file of flights for batch prediction.
    
    Supported formats: .csv, .xlsx, .xls
    
    Expected columns: airline, origin, dest, flight_date, scheduled_dep_time, distance (optional)
    """
    # Validate file extension
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    ext = "." + file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format: {ext}. Allowed: CSV, Excel (.xlsx, .xls)"
        )
    
    try:
        # Read file contents
        contents = await file.read()
        
        # Check file size
        size_mb = len(contents) / (1024 * 1024)
        if size_mb > MAX_FILE_SIZE_MB:
            raise HTTPException(
                status_code=400,
                detail=f"File too large: {size_mb:.1f}MB. Maximum: {MAX_FILE_SIZE_MB}MB"
            )
        
        # Create batch record in database
        batch_id = save_batch_upload(file.filename, f"uploads/{file.filename}")
        if not batch_id:
            batch_id = "local-" + str(hash(file.filename))
        
        # Parse file (CSV or Excel)
        try:
            df = _read_uploaded_file(contents, file.filename)
        except Exception as e:
            update_batch_status(batch_id, status="failed", error_message=f"File parse error: {e}")
            raise HTTPException(status_code=400, detail=f"Failed to parse file: {e}")
        
        # Validate required columns
        required_cols = {"airline", "origin", "dest", "flight_date", "scheduled_dep_time"}
        df_columns_lower = {col.lower().strip(): col for col in df.columns}
        missing = required_cols - set(df_columns_lower.keys())
        if missing:
            update_batch_status(batch_id, status="failed", error_message=f"Missing columns: {missing}")
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns: {missing}. Expected: airline, origin, dest, flight_date, scheduled_dep_time"
            )
        
        # Rename columns to lowercase for processing
        df.columns = [col.lower().strip() for col in df.columns]
        
        # Update batch status to processing
        update_batch_status(batch_id, status="processing", total_rows=len(df))
        
        # Process each row
        model = get_model()
        predictions = []
        delayed_count = 0
        on_time_count = 0
        errors = []
        
        for idx, row in df.iterrows():
            try:
                features = build_features_from_csv_row(row.to_dict())
                predicted_delayed, delay_prob = model.predict(features)
                
                if predicted_delayed:
                    delayed_count += 1
                else:
                    on_time_count += 1
                
                predictions.append({
                    "row_index": int(idx),
                    "airline": str(row.get("airline", "")),
                    "origin": str(row.get("origin", "")),
                    "dest": str(row.get("dest", "")),
                    "predicted_delayed": predicted_delayed,
                    "delay_probability": round(delay_prob, 4),
                })
            except Exception as e:
                errors.append({"row_index": int(idx), "error": str(e)})
        
        # Update batch record with results
        results = {
            "predictions": predictions,
            "errors": errors,
        }
        
        update_batch_status(
            batch_id,
            status="completed",
            processed_rows=len(predictions),
            delayed_count=delayed_count,
            on_time_count=on_time_count,
            results_json=json.dumps(results),
        )
        
        return BatchUploadResponse(
            batch_id=str(batch_id),
            status="completed",
            message=(
                f"Processed {len(predictions)} flights: "
                f"{delayed_count} delayed, {on_time_count} on-time. "
                f"{len(errors)} errors."
            ),
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch processing error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch processing failed: {str(e)}")


@router.get("/batch-status/{batch_id}", response_model=BatchStatusResponse)
async def get_batch_upload_status(batch_id: str):
    """Check the status and results of a batch upload."""
    record = get_batch_status(batch_id)
    
    if not record:
        raise HTTPException(status_code=404, detail=f"Batch upload not found: {batch_id}")
    
    return BatchStatusResponse(
        batch_id=record["id"],
        file_name=record["file_name"],
        status=record["status"],
        total_rows=record.get("total_rows"),
        processed_rows=record.get("processed_rows", 0),
        delayed_count=record.get("delayed_count", 0),
        on_time_count=record.get("on_time_count", 0),
        error_message=record.get("error_message"),
        created_at=str(record.get("created_at", "")),
        completed_at=str(record.get("completed_at", "")) if record.get("completed_at") else None,
    )
