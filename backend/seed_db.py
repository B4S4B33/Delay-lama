"""
Database seeding script for the US Flight Delay Predictor.
Populates airlines, airports, and model metadata in Supabase.

Usage:
    cd backend
    python seed_db.py
"""

import sys
import os
import logging

# Add backend dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import get_supabase_admin, get_supabase_client
from supabase_queries import get_all_airlines, get_all_airports

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# ─── Seed Data ──────────────────────────────────────────────

AIRLINES = [
    {"code": "Air Wisconsin Airlines Corp", "name": "Air Wisconsin Airlines Corp"},
    {"code": "Alaska Airlines Inc.", "name": "Alaska Airlines Inc."},
    {"code": "Allegiant Air", "name": "Allegiant Air"},
    {"code": "American Airlines Inc.", "name": "American Airlines Inc."},
    {"code": "Capital Cargo International", "name": "Capital Cargo International"},
    {"code": "Comair Inc.", "name": "Comair Inc."},
    {"code": "Commutair Aka Champlain Enterprises, Inc.", "name": "Commutair Aka Champlain Enterprises, Inc."},
    {"code": "Delta Air Lines Inc.", "name": "Delta Air Lines Inc."},
    {"code": "Endeavor Air Inc.", "name": "Endeavor Air Inc."},
    {"code": "Envoy Air", "name": "Envoy Air"},
    {"code": "Frontier Airlines Inc.", "name": "Frontier Airlines Inc."},
    {"code": "GoJet Airlines, LLC d/b/a United Express", "name": "GoJet Airlines, LLC d/b/a United Express"},
    {"code": "Hawaiian Airlines Inc.", "name": "Hawaiian Airlines Inc."},
    {"code": "JetBlue Airways", "name": "JetBlue Airways"},
    {"code": "Mesa Airlines Inc.", "name": "Mesa Airlines Inc."},
    {"code": "Republic Airlines", "name": "Republic Airlines"},
    {"code": "SkyWest Airlines Inc.", "name": "SkyWest Airlines Inc."},
    {"code": "Southwest Airlines Co.", "name": "Southwest Airlines Co."},
    {"code": "Spirit Air Lines", "name": "Spirit Air Lines"},
]

AIRPORTS = [
    {"code": "ATL", "name": "Hartsfield-Jackson Atlanta Intl", "city": "Atlanta", "state": "GA", "latitude": 33.6407, "longitude": -84.4277},
    {"code": "AUS", "name": "Austin-Bergstrom Intl", "city": "Austin", "state": "TX", "latitude": 30.1945, "longitude": -97.6699},
    {"code": "BNA", "name": "Nashville Intl", "city": "Nashville", "state": "TN", "latitude": 36.1263, "longitude": -86.6774},
    {"code": "BOS", "name": "Boston Logan Intl", "city": "Boston", "state": "MA", "latitude": 42.3656, "longitude": -71.0096},
    {"code": "BWI", "name": "Baltimore-Washington Intl", "city": "Baltimore", "state": "MD", "latitude": 39.1754, "longitude": -76.6684},
    {"code": "CLE", "name": "Cleveland Hopkins Intl", "city": "Cleveland", "state": "OH", "latitude": 41.4058, "longitude": -81.8539},
    {"code": "CLT", "name": "Charlotte Douglas Intl", "city": "Charlotte", "state": "NC", "latitude": 35.2140, "longitude": -80.9431},
    {"code": "CVG", "name": "Cincinnati/N KY Intl", "city": "Cincinnati", "state": "OH", "latitude": 39.0488, "longitude": -84.6678},
    {"code": "DCA", "name": "Ronald Reagan Washington Ntl", "city": "Arlington", "state": "VA", "latitude": 38.8512, "longitude": -77.0402},
    {"code": "DEN", "name": "Denver Intl", "city": "Denver", "state": "CO", "latitude": 39.8561, "longitude": -104.6737},
    {"code": "DFW", "name": "Dallas/Fort Worth Intl", "city": "Dallas", "state": "TX", "latitude": 32.8998, "longitude": -97.0403},
    {"code": "DTW", "name": "Detroit Metro Wayne County", "city": "Detroit", "state": "MI", "latitude": 42.2124, "longitude": -83.3534},
    {"code": "EWR", "name": "Newark Liberty Intl", "city": "Newark", "state": "NJ", "latitude": 40.6895, "longitude": -74.1745},
    {"code": "FLL", "name": "Fort Lauderdale-Hollywood Intl", "city": "Fort Lauderdale", "state": "FL", "latitude": 26.0742, "longitude": -80.1506},
    {"code": "HNL", "name": "Daniel K Inouye Intl", "city": "Honolulu", "state": "HI", "latitude": 21.3187, "longitude": -157.9224},
    {"code": "HOU", "name": "William P Hobby", "city": "Houston", "state": "TX", "latitude": 29.6454, "longitude": -95.2789},
    {"code": "IAD", "name": "Washington Dulles Intl", "city": "Dulles", "state": "VA", "latitude": 38.9531, "longitude": -77.4565},
    {"code": "IAH", "name": "George Bush Intercontinental", "city": "Houston", "state": "TX", "latitude": 29.9902, "longitude": -95.3368},
    {"code": "JFK", "name": "John F Kennedy Intl", "city": "New York", "state": "NY", "latitude": 40.6413, "longitude": -73.7781},
    {"code": "LAS", "name": "Harry Reid Intl", "city": "Las Vegas", "state": "NV", "latitude": 36.0840, "longitude": -115.1537},
    {"code": "LAX", "name": "Los Angeles Intl", "city": "Los Angeles", "state": "CA", "latitude": 33.9425, "longitude": -118.4081},
    {"code": "LGA", "name": "LaGuardia", "city": "New York", "state": "NY", "latitude": 40.7769, "longitude": -73.8740},
    {"code": "MCI", "name": "Kansas City Intl", "city": "Kansas City", "state": "MO", "latitude": 39.2976, "longitude": -94.7139},
    {"code": "MCO", "name": "Orlando Intl", "city": "Orlando", "state": "FL", "latitude": 28.4312, "longitude": -81.3081},
    {"code": "MDW", "name": "Chicago Midway Intl", "city": "Chicago", "state": "IL", "latitude": 41.7868, "longitude": -87.7522},
    {"code": "MEM", "name": "Memphis Intl", "city": "Memphis", "state": "TN", "latitude": 35.0421, "longitude": -89.9767},
    {"code": "MIA", "name": "Miami Intl", "city": "Miami", "state": "FL", "latitude": 25.7959, "longitude": -80.2870},
    {"code": "MKE", "name": "General Mitchell Intl", "city": "Milwaukee", "state": "WI", "latitude": 42.9472, "longitude": -87.8966},
    {"code": "MSP", "name": "Minneapolis-Saint Paul Intl", "city": "Minneapolis", "state": "MN", "latitude": 44.8848, "longitude": -93.2223},
    {"code": "MSY", "name": "Louis Armstrong New Orleans Intl", "city": "New Orleans", "state": "LA", "latitude": 29.9934, "longitude": -90.2580},
    {"code": "OAK", "name": "Oakland Intl", "city": "Oakland", "state": "CA", "latitude": 37.7213, "longitude": -122.2208},
    {"code": "ONT", "name": "Ontario Intl", "city": "Ontario", "state": "CA", "latitude": 34.0560, "longitude": -117.6012},
    {"code": "ORD", "name": "Chicago O Hare Intl", "city": "Chicago", "state": "IL", "latitude": 41.9742, "longitude": -87.9073},
    {"code": "PHL", "name": "Philadelphia Intl", "city": "Philadelphia", "state": "PA", "latitude": 39.8744, "longitude": -75.2424},
    {"code": "PHX", "name": "Phoenix Sky Harbor Intl", "city": "Phoenix", "state": "AZ", "latitude": 33.4373, "longitude": -112.0078},
    {"code": "PIT", "name": "Pittsburgh Intl", "city": "Pittsburgh", "state": "PA", "latitude": 40.4915, "longitude": -80.2329},
    {"code": "RDU", "name": "Raleigh-Durham Intl", "city": "Raleigh", "state": "NC", "latitude": 35.8776, "longitude": -78.7875},
    {"code": "SAN", "name": "San Diego Intl", "city": "San Diego", "state": "CA", "latitude": 32.7338, "longitude": -117.1933},
    {"code": "SAT", "name": "San Antonio Intl", "city": "San Antonio", "state": "TX", "latitude": 29.5337, "longitude": -98.4698},
    {"code": "SEA", "name": "Seattle-Tacoma Intl", "city": "Seattle", "state": "WA", "latitude": 47.4502, "longitude": -122.3088},
    {"code": "SFO", "name": "San Francisco Intl", "city": "San Francisco", "state": "CA", "latitude": 37.6213, "longitude": -122.3790},
    {"code": "SLC", "name": "Salt Lake City Intl", "city": "Salt Lake City", "state": "UT", "latitude": 40.7899, "longitude": -111.9791},
    {"code": "SMF", "name": "Sacramento Intl", "city": "Sacramento", "state": "CA", "latitude": 38.6954, "longitude": -121.5908},
    {"code": "SNA", "name": "John Wayne-Orange County Intl", "city": "Santa Ana", "state": "CA", "latitude": 33.6757, "longitude": -117.8678},
    {"code": "STL", "name": "St Louis Lambert Intl", "city": "St. Louis", "state": "MO", "latitude": 38.7487, "longitude": -90.3700},
    {"code": "TPA", "name": "Tampa Intl", "city": "Tampa", "state": "FL", "latitude": 27.9755, "longitude": -82.5332},
    {"code": "TUS", "name": "Tucson Intl", "city": "Tucson", "state": "AZ", "latitude": 32.1161, "longitude": -110.9410},
]


# ─── Seed Functions ─────────────────────────────────────────

def seed_airlines(client):
    """Insert airlines into the database."""
    logger.info("Seeding airlines...")
    existing = get_all_airlines()
    existing_names = {a["name"] for a in existing}
    
    new_airlines = [a for a in AIRLINES if a["name"] not in existing_names]
    
    if not new_airlines:
        logger.info(f"  All {len(AIRLINES)} airlines already present. Skipping.")
        return
    
    result = client.table("airlines").insert(new_airlines).execute()
    logger.info(f"  Inserted {len(result.data)} new airlines. Total: {len(existing) + len(result.data)}")


def seed_airports(client):
    """Insert airports into the database."""
    logger.info("Seeding airports...")
    existing = get_all_airports()
    existing_codes = {a["code"] for a in existing}
    
    new_airports = [a for a in AIRPORTS if a["code"] not in existing_codes]
    
    if not new_airports:
        logger.info(f"  All {len(AIRPORTS)} airports already present. Skipping.")
        return
    
    result = client.table("airports").insert(new_airports).execute()
    logger.info(f"  Inserted {len(result.data)} new airports. Total: {len(existing) + len(result.data)}")


def seed_model_metadata(client):
    """Insert model metadata if not present."""
    logger.info("Seeding model metadata...")
    
    result = client.table("model_metadata").select("id").eq("model_version", "1.0").execute()
    
    if result.data:
        logger.info("  Model metadata v1.0 already present. Skipping.")
        return
    
    metadata = {
        "model_version": "1.0",
        "training_data_range": "2018-2022",
        "roc_auc": 0.6720,
        "accuracy": 0.8241,
        "precision": 0.5900,
        "recall": 0.0100,
        "total_features": 9,
        "feature_list": ["Airline", "Origin", "Dest", "Distance", "Month", "DayofMonth", "DayOfWeek", "DepHour", "ArrHour"],
        "confusion_matrix": {"tn": 932298, "fp": 1391, "fn": 198212, "tp": 2002},
        "is_active": True,
        "notes": "XGBoost binary classifier trained on US domestic flights 2018-2022 (200K sample). Predicts whether arrival delay >= 15 minutes. Accuracy: 82.41%, ROC-AUC: 0.672",
    }
    
    result = client.table("model_metadata").insert([metadata]).execute()
    logger.info("  Model metadata v1.0 inserted.")


def seed_feature_importance(client):
    """Insert feature importance if not present."""
    logger.info("Seeding feature importance...")
    
    result = client.table("feature_importance").select("id").eq("model_version", "1.0").limit(1).execute()
    
    if result.data:
        logger.info("  Feature importance already present. Skipping.")
        return
    
    # Approximate importance scores from XGBoost training
    features = [
        ("Airline", 0.30, 1),
        ("DepHour", 0.22, 2),
        ("Origin", 0.18, 3),
        ("Dest", 0.12, 4),
        ("Distance", 0.08, 5),
        ("Month", 0.05, 6),
        ("ArrHour", 0.03, 7),
        ("DayOfWeek", 0.015, 8),
        ("DayofMonth", 0.005, 9),
    ]
    
    records = [
        {"model_version": "1.0", "feature_name": name, "importance_score": score, "rank": rank}
        for name, score, rank in features
    ]
    
    result = client.table("feature_importance").insert(records).execute()
    logger.info(f"  Inserted {len(result.data)} feature importance records.")


# ─── Main ───────────────────────────────────────────────────

def main():
    """Run all seed functions."""
    logger.info("=" * 60)
    logger.info("US Flight Delay Predictor — Database Seeding")
    logger.info("=" * 60)
    
    # Check for admin client
    client = get_supabase_admin()
    if client is None:
        logger.error("SUPABASE_SERVICE_KEY not set. Cannot seed database.")
        logger.info("Set SUPABASE_URL and SUPABASE_SERVICE_KEY in your .env file.")
        sys.exit(1)
    
    try:
        seed_airlines(client)
        seed_airports(client)
        seed_model_metadata(client)
        seed_feature_importance(client)
        
        logger.info("=" * 60)
        logger.info("✅ Database seeding complete!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ Seeding failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
