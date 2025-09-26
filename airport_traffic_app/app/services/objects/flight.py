from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, TypedDict


@dataclass
class FlightRecord:
    """Represents a single flight movement used for training or prediction."""

    departure_airport: str
    departure_time: datetime
    arrival_city: str
    arrival_time: datetime
    airline: str
    flight_number: str
    estimated_passengers: Optional[int] = None


class MovementDataset(TypedDict):
    """Collection of arrival and departure flights for a given purpose."""

    arrivals: List[FlightRecord]
    departures: List[FlightRecord]


class AircraftMovements(TypedDict):
    """Structured aircraft movement payload returned by the flights service."""

    airport: str
    timestamp: str
    training: MovementDataset
    prediction: MovementDataset
