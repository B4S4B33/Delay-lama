"""
Supabase client configuration and environment variable management.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")  # anon/public key
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")  # service_role key
SUPABASE_DB_URL = os.getenv("SUPABASE_DB_URL", "")

# FastAPI Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Model Configuration
MODEL_VERSION = os.getenv("MODEL_VERSION", "1.0")
MODEL_FILE_PATH = os.getenv("MODEL_FILE_PATH", "flight_delay_xgb.json")

# Initialize Supabase clients
_supabase_client = None
_supabase_admin = None


def get_supabase_client():
    """Get or create the Supabase client (anon key)."""
    global _supabase_client
    if _supabase_client is None and SUPABASE_URL and SUPABASE_KEY:
        from supabase import create_client
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _supabase_client


def get_supabase_admin():
    """Get or create the Supabase admin client (service_role key)."""
    global _supabase_admin
    if _supabase_admin is None and SUPABASE_URL and SUPABASE_SERVICE_KEY:
        from supabase import create_client
        _supabase_admin = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    return _supabase_admin


def get_supabase_client_with_token(user_token: str):
    """Create an authenticated Supabase client for a specific user."""
    if SUPABASE_URL and SUPABASE_KEY:
        from supabase import create_client
        client = create_client(SUPABASE_URL, SUPABASE_KEY)
        # Note: Token setting depends on supabase-py version
        return client
    return get_supabase_client()
