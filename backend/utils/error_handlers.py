"""
Custom error handlers and exception classes.
"""

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


class FlightDelayError(Exception):
    """Base exception for flight delay predictor."""
    def __init__(self, message: str, code: str = "UNKNOWN_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class ModelNotLoadedError(FlightDelayError):
    """ML model failed to load."""
    def __init__(self):
        super().__init__("ML model is not loaded. Check model file path.", "MODEL_NOT_LOADED")


class InvalidInputError(FlightDelayError):
    """Invalid input data."""
    def __init__(self, message: str):
        super().__init__(message, "INVALID_INPUT")


class DatabaseError(FlightDelayError):
    """Database operation failed."""
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(message, "DATABASE_ERROR")


class RouteNotFoundError(FlightDelayError):
    """Route not found in training data."""
    def __init__(self, origin: str, dest: str):
        super().__init__(
            f"Route {origin}→{dest} not found in training data",
            "ROUTE_NOT_FOUND"
        )


class AirlineNotFoundError(FlightDelayError):
    """Airline not found in training data."""
    def __init__(self, airline: str):
        super().__init__(
            f"Airline '{airline}' not found in training data",
            "AIRLINE_NOT_FOUND"
        )


async def flight_delay_error_handler(request: Request, exc: FlightDelayError):
    """Handle custom FlightDelayError exceptions."""
    status_code = 400
    if isinstance(exc, (RouteNotFoundError, AirlineNotFoundError)):
        status_code = 404
    elif isinstance(exc, ModelNotLoadedError):
        status_code = 503
    elif isinstance(exc, DatabaseError):
        status_code = 502
    
    return JSONResponse(
        status_code=status_code,
        content={"detail": exc.message, "code": exc.code}
    )
