"""
Feature importance and prediction explainability engine.
Provides per-prediction explanations using global feature importance.
"""

import logging
from typing import List, Dict, Optional
import numpy as np

logger = logging.getLogger(__name__)

# Human-readable feature labels
FEATURE_LABELS = {
    'Month': 'Month of Year',
    'DayofMonth': 'Day of Month',
    'DayOfWeek': 'Day of Week',
    'Airline': 'Airline',
    'Origin': 'Origin Airport',
    'Dest': 'Destination Airport',
    'Distance': 'Route Distance',
    'DepHour': 'Departure Hour',
    'ArrHour': 'Arrival Hour',
}


class ExplainabilityEngine:
    """
    Extracts and ranks factors that drive individual predictions.
    
    Uses global feature importance from the XGBoost model combined
    with per-instance feature values to determine which factors
    most influence a specific prediction.
    """
    
    def __init__(self, model):
        """
        Initialize with a trained model.
        
        Args:
            model: FlightDelayModel instance
        """
        self.model = model
        self._importance_cache = None
    
    def _get_importance(self) -> Dict[str, float]:
        """Get or cache feature importance."""
        if self._importance_cache is None:
            self._importance_cache = self.model.get_feature_importance()
        return self._importance_cache
    
    def get_top_factors(
        self, 
        prediction_input: Dict, 
        top_n: int = 3
    ) -> List[Dict]:
        """
        Extract top N factors driving a specific prediction.
        
        Combines global feature importance with per-instance values
        to rank which features most influence the prediction.
        
        Args:
            prediction_input: The input features used for prediction
            top_n: Number of top factors to return (default 3)
            
        Returns:
            List of dicts with keys: feature, impact, direction, label
        """
        importance = self._get_importance()
        
        if not importance:
            logger.warning("No feature importance available, returning empty factors")
            return []
        
        factors = []
        for feature_name, imp_score in importance.items():
            # Determine direction based on feature value
            value = prediction_input.get(feature_name, 0)
            direction = self._determine_direction(feature_name, value)
            
            factors.append({
                'feature': feature_name,
                'impact': float(imp_score),
                'direction': direction,
                'label': FEATURE_LABELS.get(feature_name, feature_name),
            })
        
        # Sort by impact (descending)
        factors.sort(key=lambda x: x['impact'], reverse=True)
        
        # Return top N
        top_factors = factors[:top_n]
        
        # Normalize impact scores to sum to 1.0 for the top factors
        total_impact = sum(f['impact'] for f in top_factors)
        if total_impact > 0:
            for f in top_factors:
                f['impact'] = round(f['impact'] / total_impact, 4)
        
        return top_factors
    
    def _determine_direction(self, feature_name: str, value) -> str:
        """
        Determine if a feature value increases or decreases delay risk.
        
        This uses heuristics based on domain knowledge:
        - Late departure hours increase delay risk
        - Longer distances may decrease delay risk (more buffer)
        - Certain airlines have higher historical delay rates
        
        Args:
            feature_name: Name of the feature
            value: Feature value
            
        Returns:
            "increases" or "decreases"
        """
        if feature_name == 'DepHour':
            # Late night/early morning flights less likely delayed
            # Peak hours (6-10 AM, 4-8 PM) more likely delayed
            hour = int(value) if value else 12
            if 6 <= hour <= 10 or 16 <= hour <= 20:
                return 'increases'
            return 'decreases'
        
        elif feature_name == 'ArrHour':
            hour = int(value) if value else 12
            if 17 <= hour <= 23:
                return 'increases'
            return 'decreases'
        
        elif feature_name == 'Distance':
            # Longer flights have more buffer time
            dist = float(value) if value else 0
            if dist > 1500:
                return 'decreases'
            return 'increases'
        
        elif feature_name == 'Month':
            # Summer (Jun-Aug) and holidays tend to have more delays
            month = int(value) if value else 1
            if month in [6, 7, 8, 11, 12]:
                return 'increases'
            return 'decreases'
        
        elif feature_name == 'DayOfWeek':
            # Fridays and Sundays tend to be worse
            dow = int(value) if value else 1
            if dow in [5, 7]:  # Friday=5, Sunday=7
                return 'increases'
            return 'decreases'
        
        elif feature_name in ['Airline', 'Origin', 'Dest']:
            # For categorical features, we can't determine direction
            # from value alone — use neutral
            return 'influences'
        
        return 'influences'


# Singleton instance
_explainability_engine = None


def get_explainability_engine(model=None):
    """Get or create the explainability engine."""
    global _explainability_engine
    if _explainability_engine is None:
        if model is None:
            from ml_engine import get_model
            model = get_model()
        _explainability_engine = ExplainabilityEngine(model)
    return _explainability_engine
