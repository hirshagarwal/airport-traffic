from datetime import datetime, timedelta

from .objects.flight import AircraftMovements, FlightRecord, MovementDataset


def _build_mock_flight(
    *,
    base_time: datetime,
    departure_airport: str,
    departure_offset_minutes: int,
    arrival_city: str,
    arrival_offset_minutes: int,
    base_passengers: int,
) -> FlightRecord:
    return FlightRecord(
        departure_airport=departure_airport,
        departure_time=base_time + timedelta(minutes=departure_offset_minutes),
        arrival_city=arrival_city,
        arrival_time=base_time + timedelta(minutes=arrival_offset_minutes),
        estimated_passengers=base_passengers,
    )


def get_aircraft_movements(airport_code: str, dt: datetime) -> AircraftMovements:
    """Return mocked aircraft movement data for arrivals and departures."""
    airport = airport_code.upper()

    arrivals = [
        _build_mock_flight(
            base_time=dt,
            departure_airport="SEA",
            departure_offset_minutes=-180,
            arrival_city=airport,
            arrival_offset_minutes=-60,
            base_passengers=140,
        ),
        _build_mock_flight(
            base_time=dt,
            departure_airport="DEN",
            departure_offset_minutes=-240,
            arrival_city=airport,
            arrival_offset_minutes=-30,
            base_passengers=160,
        ),
    ]

    departures = [
        _build_mock_flight(
            base_time=dt,
            departure_airport=airport,
            departure_offset_minutes=30,
            arrival_city="BOS",
            arrival_offset_minutes=240,
            base_passengers=150,
        ),
        _build_mock_flight(
            base_time=dt,
            departure_airport=airport,
            departure_offset_minutes=75,
            arrival_city="MIA",
            arrival_offset_minutes=315,
            base_passengers=170,
        ),
    ]

    # Split into training and prediction buckets; this keeps room to add real data sources later.
    training_dataset: MovementDataset = {
        "arrivals": arrivals[:1],
        "departures": departures[:1],
    }
    prediction_dataset: MovementDataset = {
        "arrivals": arrivals[1:],
        "departures": departures[1:],
    }

    return AircraftMovements(
        airport=airport,
        timestamp=dt.isoformat() + "Z",
        training=training_dataset,
        prediction=prediction_dataset,
    )
