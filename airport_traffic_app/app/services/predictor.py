from datetime import datetime
from typing import Iterable

from .flights_api import get_aircraft_movements
from .objects.flight import FlightRecord
from .tsa_api import get_tsa_throughput


def _sum_passengers(flights: Iterable[FlightRecord]) -> int:
    return sum(flight.estimated_passengers for flight in flights)


def estimate_traffic(airport_code: str, dt: datetime) -> int:
    """Combine mocked TSA throughput and flight movements for a simple estimate."""
    tsa_data = get_tsa_throughput(airport_code, dt)
    flights_data = get_aircraft_movements(airport_code, dt)

    prediction_flights = flights_data["prediction"]
    passenger_signal = _sum_passengers(prediction_flights["arrivals"]) + _sum_passengers(
        prediction_flights["departures"]
    )

    throughput = tsa_data["passengers"]

    # Dummy heuristic: passengers + throughput adjusted for predicted passenger volumes.
    return int(throughput + passenger_signal * 1.5)
