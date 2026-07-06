"""
Batch CSV/Excel processing engine for flight delay predictions.
"""

import io
import json
import logging
import pandas as pd
from typing import Dict, List, Optional

from ml_engine import get_model
from utils.feature_engineering import build_features_from_csv_row

logger = logging.getLogger(__name__)


class BatchProcessor:
    """Processes CSV or Excel files of flights for batch delay prediction."""
    
    def __init__(self, file_content: bytes, filename: str = ""):
        """
        Initialize with file bytes.
        
        Args:
            file_content: Raw bytes of the CSV or Excel file
            filename: Original filename (used to determine format)
        """
        ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        
        if ext == ".csv":
            self.df = pd.read_csv(io.BytesIO(file_content))
        elif ext in (".xlsx", ".xls"):
            engine = "openpyxl" if ext == ".xlsx" else "xlrd"
            self.df = pd.read_excel(io.BytesIO(file_content), engine=engine)
        else:
            # Default to CSV
            self.df = pd.read_csv(io.BytesIO(file_content))
        
        # Normalize column names
        self.df.columns = [col.lower().strip() for col in self.df.columns]
    
    def validate(self) -> Optional[str]:
        """
        Validate the file has required columns.
        
        Returns:
            Error message if invalid, None if valid
        """
        required = {"airline", "origin", "dest", "flight_date", "scheduled_dep_time"}
        available = set(self.df.columns)
        missing = required - available
        if missing:
            return f"Missing required columns: {missing}"
        return None
    
    def process(self) -> Dict:
        """
        Process all rows and return prediction results.
        
        Returns:
            Dict with total_rows, delayed_count, on_time_count, predictions, errors
        """
        model = get_model()
        
        results = []
        delayed_count = 0
        on_time_count = 0
        errors = []
        
        for idx, row in self.df.iterrows():
            try:
                features = build_features_from_csv_row(row.to_dict())
                predicted_delayed, delay_prob = model.predict(features)
                
                if predicted_delayed:
                    delayed_count += 1
                else:
                    on_time_count += 1
                
                results.append({
                    "row_index": int(idx),
                    "airline": str(row.get("airline", "")),
                    "origin": str(row.get("origin", "")),
                    "dest": str(row.get("dest", "")),
                    "predicted_delayed": predicted_delayed,
                    "delay_probability": round(delay_prob, 4),
                })
            except Exception as e:
                errors.append({
                    "row_index": int(idx),
                    "error": str(e),
                })
        
        return {
            "total_rows": len(self.df),
            "delayed_count": delayed_count,
            "on_time_count": on_time_count,
            "predictions": results,
            "errors": errors,
        }
