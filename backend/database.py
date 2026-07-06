"""
Database connection helpers and query utilities.
Wraps Supabase client for common database operations.
"""

import logging
from typing import Optional, List, Dict, Any
from config import get_supabase_client, get_supabase_admin

logger = logging.getLogger(__name__)


class Database:
    """Wrapper around Supabase client for database operations."""
    
    def __init__(self):
        self._client = None
        self._admin = None
    
    @property
    def client(self):
        if self._client is None:
            self._client = get_supabase_client()
        return self._client
    
    @property
    def admin(self):
        if self._admin is None:
            self._admin = get_supabase_admin()
        return self._admin
    
    def is_connected(self) -> bool:
        """Check if database is accessible."""
        try:
            if self.client is None:
                return False
            result = self.client.table("airlines").select("id").limit(1).execute()
            return True
        except Exception as e:
            logger.warning(f"Database connection check failed: {e}")
            return False
    
    # ─── Airlines ──────────────────────────────────────
    def get_airline_by_code(self, code: str) -> Optional[Dict]:
        """Fetch airline record by code."""
        try:
            result = self.client.table("airlines").select("*").eq("code", code).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error fetching airline {code}: {e}")
            return None
    
    def get_all_airlines(self) -> List[Dict]:
        """Fetch all airlines."""
        try:
            result = self.client.table("airlines").select("code, name").order("name").execute()
            return result.data
        except Exception as e:
            logger.error(f"Error fetching airlines: {e}")
            return []
    
    # ─── Airports ──────────────────────────────────────
    def get_airport_by_code(self, code: str) -> Optional[Dict]:
        """Fetch airport record by code."""
        try:
            result = self.client.table("airports").select("*").eq("code", code).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error fetching airport {code}: {e}")
            return None
    
    def get_all_airports(self) -> List[Dict]:
        """Fetch all airports."""
        try:
            result = self.client.table("airports").select("code, name, city, state").order("code").execute()
            return result.data
        except Exception as e:
            logger.error(f"Error fetching airports: {e}")
            return []
    
    # ─── Routes ────────────────────────────────────────
    def get_route(self, origin_code: str, dest_code: str) -> Optional[Dict]:
        """Fetch route with stats by origin and destination codes."""
        try:
            origin = self.get_airport_by_code(origin_code)
            dest = self.get_airport_by_code(dest_code)
            if not origin or not dest:
                return None
            
            result = self.client.table("routes").select("*").eq("origin_id", origin["id"]).eq("dest_id", dest["id"]).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error fetching route {origin_code}-{dest_code}: {e}")
            return None
    
    # ─── Predictions ───────────────────────────────────
    def save_prediction(self, data: Dict) -> Optional[str]:
        """Save a prediction record, return UUID."""
        try:
            result = self.client.table("predictions").insert(data).execute()
            return result.data[0]["id"] if result.data else None
        except Exception as e:
            logger.error(f"Error saving prediction: {e}")
            return None
    
    def save_explainability_factors(self, prediction_id: str, factors: List[Dict]) -> bool:
        """Save explainability factors for a prediction."""
        try:
            records = [
                {
                    "prediction_id": prediction_id,
                    "feature_name": f["feature"],
                    "impact_magnitude": f["impact"],
                    "direction": f["direction"],
                    "rank": i + 1
                }
                for i, f in enumerate(factors)
            ]
            result = self.client.table("explainability_factors").insert(records).execute()
            return len(result.data) == len(records)
        except Exception as e:
            logger.error(f"Error saving factors: {e}")
            return False
    
    # ─── Batch Uploads ─────────────────────────────────
    def save_batch_upload(self, data: Dict) -> Optional[str]:
        """Create a batch upload record, return UUID."""
        try:
            result = self.client.table("batch_uploads").insert(data).execute()
            return result.data[0]["id"] if result.data else None
        except Exception as e:
            logger.error(f"Error saving batch upload: {e}")
            return None
    
    def update_batch_upload(self, batch_id: str, data: Dict) -> bool:
        """Update a batch upload record."""
        try:
            result = self.client.table("batch_uploads").update(data).eq("id", batch_id).execute()
            return True
        except Exception as e:
            logger.error(f"Error updating batch {batch_id}: {e}")
            return False
    
    def get_batch_upload(self, batch_id: str) -> Optional[Dict]:
        """Fetch batch upload status."""
        try:
            result = self.client.table("batch_uploads").select("*").eq("id", batch_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error fetching batch {batch_id}: {e}")
            return None
    
    # ─── Model Metadata ────────────────────────────────
    def get_active_model_metadata(self) -> Optional[Dict]:
        """Fetch the active model's metadata."""
        try:
            result = self.client.table("model_metadata").select("*").eq("is_active", True).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error fetching model metadata: {e}")
            return None
    
    def get_feature_importance(self, model_version: str) -> List[Dict]:
        """Fetch feature importance for a model version."""
        try:
            result = self.client.table("feature_importance").select("*").eq("model_version", model_version).order("rank").execute()
            return result.data
        except Exception as e:
            logger.error(f"Error fetching feature importance: {e}")
            return []


# Singleton instance
db = Database()
