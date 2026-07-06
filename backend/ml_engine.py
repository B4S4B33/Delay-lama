"""
ML Model loading and prediction engine.
Handles XGBoost model lifecycle and inference.
"""

import os
import logging
import pandas as pd
import numpy as np
import xgboost as xgb
import joblib
from typing import Tuple, Dict, Optional, List

logger = logging.getLogger(__name__)

# Feature columns in the exact order the model expects
FEATURE_COLUMNS = [
    'Airline', 'Origin', 'Dest',
    'Distance', 'Month', 'DayofMonth',
    'DayOfWeek', 'DepHour', 'ArrHour'
]

# Categorical columns that need special dtype handling
CATEGORICAL_COLUMNS = ['Airline', 'Origin', 'Dest']


class FlightDelayModel:
    """
    XGBoost-based flight delay prediction model.

    Predicts whether a flight will be delayed by 15+ minutes at arrival.
    Uses XGBoost native categorical support for airline and airport features.
    """

    def __init__(self, model_path: str):
        """
        Load the XGBoost model from file.

        Args:
            model_path: Path to the model file (.json or .joblib)
        """
        self.model_path = model_path
        self.model = None
        self._load_model()

    def _load_model(self):
        """Load model from file (supports both .json and .joblib formats)."""
        if not os.path.exists(self.model_path):
            logger.error(f"Model file not found: {self.model_path}")
            raise FileNotFoundError(f"Model file not found: {self.model_path}")

        try:
            if self.model_path.endswith('.joblib'):
                self.model = joblib.load(self.model_path)
                logger.info(f"Loaded model from joblib: {self.model_path}")
            elif self.model_path.endswith('.json'):
                self.model = xgb.XGBClassifier()
                self.model.load_model(self.model_path)
                logger.info(f"Loaded model from JSON: {self.model_path}")
            else:
                raise ValueError(f"Unsupported model format: {self.model_path}")
        except FileNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise

    def _build_dataframe(self, features: Dict) -> pd.DataFrame:
        """
        Build a properly typed DataFrame from a feature dictionary.

        Args:
            features: Dictionary of feature values

        Returns:
            DataFrame with correct dtypes
        """
        df = pd.DataFrame([features])

        for col in FEATURE_COLUMNS:
            if col not in df.columns:
                raise ValueError(f"Missing required feature: {col}")

        df = df[FEATURE_COLUMNS]

        for col in CATEGORICAL_COLUMNS:
            df[col] = df[col].astype('category')

        numeric_cols = ['Month', 'DayofMonth', 'DayOfWeek', 'Distance', 'DepHour', 'ArrHour']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').astype('float32')

        return df

    def predict(self, features: Dict) -> Tuple[bool, float]:
        """
        Predict delay probability for a single flight.

        Args:
            features: Dictionary with keys matching FEATURE_COLUMNS

        Returns:
            Tuple of (predicted_delayed: bool, delay_probability: float)
        """
        try:
            df = self._build_dataframe(features)
            proba = self.model.predict_proba(df)[0][1]
            predicted_delayed = bool(proba > 0.5)
            return predicted_delayed, float(proba)
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise RuntimeError(f"Prediction failed: {e}")

    def predict_batch(self, features_list: List[Dict]) -> List[Tuple[bool, float]]:
        """
        Predict delay for multiple flights.

        Args:
            features_list: List of feature dictionaries

        Returns:
            List of (predicted_delayed, delay_probability) tuples
        """
        try:
            df = pd.DataFrame(features_list)
            for col in CATEGORICAL_COLUMNS:
                df[col] = df[col].astype('category')
            df = df[FEATURE_COLUMNS]
            probas = self.model.predict_proba(df)[:, 1]
            return [(bool(p > 0.5), float(p)) for p in probas]
        except Exception as e:
            logger.error(f"Batch prediction failed: {e}")
            raise RuntimeError(f"Batch prediction failed: {e}")

    def get_feature_importance(self) -> Dict[str, float]:
        """Get global feature importance scores."""
        try:
            importance = self.model.feature_importances_
            return {feat: float(imp) for feat, imp in zip(FEATURE_COLUMNS, importance)}
        except Exception as e:
            logger.warning(f"Could not get feature importance: {e}")
            return {}

    def get_num_features(self) -> int:
        """Return number of features the model expects."""
        return len(FEATURE_COLUMNS)


# ─── Global Model Singleton ─────────────────────────────────

_model_instance: Optional[FlightDelayModel] = None


def get_model() -> FlightDelayModel:
    """Get or create the global model instance. Searches multiple paths."""
    global _model_instance
    if _model_instance is not None:
        return _model_instance

    from config import MODEL_FILE_PATH

    # Build a list of candidate paths to search
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(backend_dir)

    candidate_paths = [
        MODEL_FILE_PATH,                                                         # as-is from env
        os.path.join(backend_dir, MODEL_FILE_PATH),                              # relative to backend/
        os.path.join(project_root, MODEL_FILE_PATH),                             # relative to project root
        os.path.join(project_root, 'output', 'flight_delay_xgb.json'),          # project/output/
        os.path.join(backend_dir, 'flight_delay_xgb.json'),                      # backend/
    ]

    for path in candidate_paths:
        if os.path.exists(path):
            _model_instance = FlightDelayModel(path)
            return _model_instance

    raise FileNotFoundError(
        f"Could not find model file. Searched: {candidate_paths}"
    )
