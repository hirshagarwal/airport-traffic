from datetime import datetime

from app import create_app
from app.services.flights_api import get_aircraft_movements
from app.services.objects.flight import FlightRecord


def test_index_route_renders_template():
    app = create_app()
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert b"Airport Traffic Estimator" in response.data


def test_estimate_route_returns_prediction():
    app = create_app()
    client = app.test_client()

    response = client.get("/estimate/JFK")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["airport"] == "JFK"
    assert "predicted_passenger_load" in payload
    assert isinstance(payload["predicted_passenger_load"], int)


def test_flight_service_returns_structured_data():
    reference_time = datetime.utcnow()
    data = get_aircraft_movements("LAX", reference_time)

    assert data["airport"] == "LAX"
    assert len(data["training"]["arrivals"]) == 1
    assert len(data["training"]["departures"]) == 1
    assert len(data["prediction"]["arrivals"]) == 1
    assert len(data["prediction"]["departures"]) == 1
    assert isinstance(data["prediction"]["arrivals"][0], FlightRecord)
