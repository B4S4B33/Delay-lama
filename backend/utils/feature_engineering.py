"""
Feature engineering utilities for transforming raw flight data
into model-ready features. Reuses logic from the training notebook.
"""

import logging
from typing import Dict, Optional
from datetime import date, time

logger = logging.getLogger(__name__)


def extract_departure_hour(scheduled_dep_time: time) -> int:
    """
    Extract departure hour from scheduled departure time.
    
    Args:
        scheduled_dep_time: Python time object
        
    Returns:
        Hour as integer (0-23)
    """
    return scheduled_dep_time.hour


def extract_arrival_hour(distance: int, scheduled_dep_time: time) -> int:
    """
    Estimate arrival hour from departure time and distance.
    
    Uses a simple heuristic: average commercial flight speed ~500 mph
    plus 30 minutes for taxi/takeoff/landing.
    
    Args:
        distance: Route distance in miles
        scheduled_dep_time: Scheduled departure time
        
    Returns:
        Estimated arrival hour (0-23)
    """
    # Estimate flight duration in hours
    avg_speed_mph = 500
    taxi_time_hours = 0.5  # 30 minutes
    
    flight_hours = (distance / avg_speed_mph) + taxi_time_hours
    
    # Calculate arrival time
    dep_minutes = scheduled_dep_time.hour * 60 + scheduled_dep_time.minute
    arr_minutes = dep_minutes + int(flight_hours * 60)
    
    # Handle day boundary
    arr_hour = (arr_minutes // 60) % 24
    
    return arr_hour


def build_features(
    airline: str,
    origin: str,
    dest: str,
    flight_date: date,
    scheduled_dep_time: time,
    distance: Optional[int] = None,
) -> Dict:
    """
    Build model feature dictionary from raw flight inputs.
    
    Transforms user-facing inputs into the exact feature format
    expected by the XGBoost model.
    
    Args:
        airline: Airline name (e.g., "United Airlines")
        origin: Origin airport code (e.g., "ORD")
        dest: Destination airport code (e.g., "LAX")
        flight_date: Flight date
        scheduled_dep_time: Scheduled departure time
        distance: Route distance in miles (optional, estimated if not provided)
        
    Returns:
        Dictionary of features matching FEATURE_COLUMNS order
    """
    # Extract date components
    month = flight_date.month
    day_of_month = flight_date.day
    # Python weekday(): Monday=0, Sunday=6
    # Training data: Monday=1, Sunday=7
    day_of_week = flight_date.weekday() + 1
    
    # Extract time components
    dep_hour = extract_departure_hour(scheduled_dep_time)
    
    # Estimate distance if not provided
    if distance is None:
        distance = 800  # Default average domestic flight distance
    
    # Estimate arrival hour
    arr_hour = extract_arrival_hour(distance, scheduled_dep_time)
    
    return {
        'Month': month,
        'DayofMonth': day_of_month,
        'DayOfWeek': day_of_week,
        'Airline': airline,
        'Origin': origin.upper(),
        'Dest': dest.upper(),
        'Distance': float(distance),
        'DepHour': dep_hour,
        'ArrHour': arr_hour,
    }


def build_features_from_csv_row(row: Dict) -> Dict:
    """
    Build model features from a CSV row dictionary.
    
    Expected CSV columns: airline, origin, dest, flight_date, 
    scheduled_dep_time, distance (optional)
    
    Args:
        row: Dictionary from CSV row
        
    Returns:
        Dictionary of model features
    """
    from datetime import datetime
    
    # Parse date
    flight_date_str = row.get('flight_date', row.get('FlightDate', ''))
    if isinstance(flight_date_str, str):
        flight_date = datetime.strptime(flight_date_str, '%Y-%m-%d').date()
    else:
        flight_date = flight_date_str
    
    # Parse time
    dep_time_str = row.get('scheduled_dep_time', row.get('CRSDepTime', ''))
    if isinstance(dep_time_str, str):
        # Handle both "HH:MM" and "HHMM" formats
        if ':' in dep_time_str:
            scheduled_dep_time = datetime.strptime(dep_time_str, '%H:%M').time()
        else:
            hour = int(dep_time_str) // 100
            minute = int(dep_time_str) % 100
            scheduled_dep_time = time(hour, minute)
    elif isinstance(dep_time_str, time):
        scheduled_dep_time = dep_time_str
    else:
        # Assume HHMM integer format
        hour = int(dep_time_str) // 100
        minute = int(dep_time_str) % 100
        scheduled_dep_time = time(hour, minute)
    
    airline = row.get('airline', row.get('Airline', ''))
    origin = row.get('origin', row.get('Origin', ''))
    dest = row.get('dest', row.get('Dest', ''))
    distance = row.get('distance', row.get('Distance', None))
    
    if distance:
        distance = int(float(distance))
    
    return build_features(
        airline=airline,
        origin=origin,
        dest=dest,
        flight_date=flight_date,
        scheduled_dep_time=scheduled_dep_time,
        distance=distance,
    )
