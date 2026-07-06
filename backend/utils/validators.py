"""
Input validation utilities for flight data.
"""

import logging
from typing import Optional, Set

logger = logging.getLogger(__name__)

# Exact airline names from training data (robikscube/flight-delay-dataset-20182022)
KNOWN_AIRLINES: Set[str] = {
    "Air Wisconsin Airlines Corp",
    "Alaska Airlines Inc.",
    "Allegiant Air",
    "American Airlines Inc.",
    "Capital Cargo International",
    "Comair Inc.",
    "Commutair Aka Champlain Enterprises, Inc.",
    "Delta Air Lines Inc.",
    "Endeavor Air Inc.",
    "Envoy Air",
    "Frontier Airlines Inc.",
    "GoJet Airlines, LLC d/b/a United Express",
    "Hawaiian Airlines Inc.",
    "JetBlue Airways",
    "Mesa Airlines Inc.",
    "Republic Airlines",
    "SkyWest Airlines Inc.",
    "Southwest Airlines Co.",
    "Spirit Air Lines",
}

# Known US airport codes from training data (358 total, major ones listed)
KNOWN_AIRPORTS: Set[str] = {
    "ATL", "AUS", "BNA", "BOS", "BWI", "CLE", "CLT", "CVG", "DCA",
    "DEN", "DFW", "DTW", "EWR", "FLL", "HNL", "HOU", "IAD", "IAH",
    "JFK", "LAS", "LAX", "LGA", "MCI", "MCO", "MDW", "MEM", "MIA",
    "MKE", "MSP", "MSY", "OAK", "ONT", "ORD", "PHL", "PHX", "PIT",
    "RDU", "SAN", "SAT", "SEA", "SFO", "SLC", "SMF", "SNA", "STL",
    "TPA", "TUS",
}


def validate_airline(airline: str) -> bool:
    """Validate airline name against known airlines from training data."""
    return airline in KNOWN_AIRLINES


def validate_airport(code: str) -> bool:
    """Validate 3-letter airport code."""
    return code.upper() in KNOWN_AIRPORTS


def normalize_airline(airline: str) -> Optional[str]:
    """
    Normalize airline name to match exact training data format.
    Handles common user-friendly names by mapping to training names.
    """
    # Try exact match first
    if airline in KNOWN_AIRLINES:
        return airline

    # Try case-insensitive match
    airline_lower = airline.lower().strip()
    for known in KNOWN_AIRLINES:
        if known.lower() == airline_lower:
            return known

    # Common user-friendly name mappings
    ALIAS_MAP = {
        "united airlines": "GoJet Airlines, LLC d/b/a United Express",
        "united": "GoJet Airlines, LLC d/b/a United Express",
        "american airlines": "American Airlines Inc.",
        "american": "American Airlines Inc.",
        "delta air lines": "Delta Air Lines Inc.",
        "delta": "Delta Air Lines Inc.",
        "southwest airlines": "Southwest Airlines Co.",
        "southwest": "Southwest Airlines Co.",
        "alaska airlines": "Alaska Airlines Inc.",
        "alaska": "Alaska Airlines Inc.",
        "jetblue airways": "JetBlue Airways",
        "jetblue": "JetBlue Airways",
        "spirit airlines": "Spirit Air Lines",
        "spirit": "Spirit Air Lines",
        "frontier airlines": "Frontier Airlines Inc.",
        "frontier": "Frontier Airlines Inc.",
        "hawaiian airlines": "Hawaiian Airlines Inc.",
        "hawaiian": "Hawaiian Airlines Inc.",
        "allegiant air": "Allegiant Air",
        "allegiant": "Allegiant Air",
        "endeavor air": "Endeavor Air Inc.",
        "envoy air": "Envoy Air",
        "mesa airlines": "Mesa Airlines Inc.",
        "skywest airlines": "SkyWest Airlines Inc.",
        "skywest": "SkyWest Airlines Inc.",
        "republic airlines": "Republic Airlines",
        "republic airways": "Republic Airlines",
    }

    mapped = ALIAS_MAP.get(airline_lower)
    if mapped:
        return mapped

    # Try partial match as last resort
    for known in KNOWN_AIRLINES:
        if airline_lower in known.lower() or known.lower() in airline_lower:
            return known

    return None


def normalize_airport(code: str) -> Optional[str]:
    """Normalize airport code to uppercase 3-letter."""
    code = code.strip().upper()
    if len(code) == 3 and code.isalpha():
        return code
    return None
