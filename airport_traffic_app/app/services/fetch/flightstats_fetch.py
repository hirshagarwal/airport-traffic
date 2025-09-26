"""Utilities for retrieving JFK departure information."""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

try:  # Prefer requests when available.
    import requests
    from requests import Session as _RequestsSession
except ImportError:  # pragma: no cover - requests may be absent in some environments.
    requests = None  # type: ignore
    _RequestsSession = Any  # type: ignore

from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

try:  # Prefer package-relative import when available.
    from ..objects.flight import FlightRecord  # type: ignore[import]  # pragma: no cover
except (ImportError, ValueError):
    from objects.flight import FlightRecord  # type: ignore[import]  # pragma: no cover

FLIGHTSTATS_DEPARTURES_URL = "https://www.flightstats.com/v2/flight-tracker/departures"

# FlightStats serves dynamic content and may block non-browser clients unless a
# reasonable User-Agent and Accept headers are provided.
_DEFAULT_HEADERS: Dict[str, str] = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;"
        "q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.flightstats.com/",
}

_NEXT_DATA_PATTERN = re.compile(
    r"__NEXT_DATA__\s*=\s*(\{.*?\})\s*;__NEXT_LOADED_PAGES__",
    re.DOTALL,
)
_FLIGHTS_PATH = ("props", "initialState", "flightTracker", "route", "flights")


@dataclass(frozen=True)
class DepartureQuery:
    year: int
    month: int
    day: int
    hour: int

    def as_params(self) -> Dict[str, str]:
        return {
            "year": str(self.year),
            "month": str(self.month),
            "date": str(self.day),
            "hour": str(self.hour),
        }


def _validate_query(query: DepartureQuery) -> None:
    if not (1 <= query.month <= 12):
        raise ValueError("month must be between 1 and 12")
    if not (1 <= query.day <= 31):
        raise ValueError("day must be between 1 and 31")
    if not (0 <= query.hour <= 23):
        raise ValueError("hour must be between 0 and 23")


def _http_get(
    url: str,
    *,
    params: Dict[str, str],
    headers: Dict[str, str],
    timeout: float,
    session: Optional[_RequestsSession],
) -> str:
    if requests is not None:
        request_session = session or requests.Session()
        try:
            response = request_session.get(url, params=params, headers=headers, timeout=timeout)
            response.raise_for_status()
            return response.text
        finally:
            if session is None:
                request_session.close()

    if session is not None:
        raise RuntimeError("An explicit session requires the requests library to be installed.")

    request = Request(f"{url}?{urlencode(params)}", headers=headers)
    try:
        with urlopen(request, timeout=timeout) as resp:  # nosec B310 - trusted domain
            return resp.read().decode("utf-8", errors="replace")
    except HTTPError as exc:  # pragma: no cover - network dependent
        raise RuntimeError(f"FlightStats request failed with status {exc.code}") from exc
    except URLError as exc:  # pragma: no cover - network dependent
        raise RuntimeError("Unable to reach FlightStats") from exc


def _extract_next_data(html: str) -> Dict[str, Any]:
    match = _NEXT_DATA_PATTERN.search(html)
    if not match:
        raise ValueError("Could not locate FlightStats payload in response HTML.")
    return json.loads(match.group(1))


def _walk_path(root: Dict[str, Any], path: tuple[str, ...]) -> Any:
    current: Any = root
    for segment in path:
        if not isinstance(current, dict) or segment not in current:
            raise KeyError(f"Missing segment '{segment}' while traversing Next.js payload")
        current = current[segment]
    return current


def _parse_sort_time(value: Any) -> datetime:
    if not isinstance(value, str) or not value:
        raise ValueError("Flight record missing sortTime value")
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    parsed = datetime.fromisoformat(normalized)
    return parsed.replace(tzinfo=None)


def _compose_arrival_datetime(departure_dt: datetime, arrival_payload: Any) -> datetime:
    if not isinstance(arrival_payload, dict):
        return departure_dt
    time_24 = arrival_payload.get("time24")
    if not isinstance(time_24, str) or ":" not in time_24:
        return departure_dt
    parts = time_24.split(":")
    try:
        hour = int(parts[0])
        minute = int(parts[1])
    except (ValueError, IndexError):
        return departure_dt
    arrival_dt = departure_dt.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if arrival_dt < departure_dt:
        arrival_dt += timedelta(days=1)
    return arrival_dt


def _parse_flight_record(raw: Dict[str, Any], *, departure_airport: str) -> FlightRecord:
    departure_dt = _parse_sort_time(raw.get("sortTime"))
    arrival_dt = _compose_arrival_datetime(departure_dt, raw.get("arrivalTime"))

    airport_payload = raw.get("airport") or {}
    carrier_payload = raw.get("carrier") or {}

    arrival_city = (
        airport_payload.get("city")
        or airport_payload.get("name")
        or airport_payload.get("fs")
        or ""
    )
    airline = carrier_payload.get("name") or carrier_payload.get("fs") or ""
    carrier_code = carrier_payload.get("fs", "").strip()
    flight_number = carrier_payload.get("flightNumber", "").strip()
    combined_identifier = " ".join(part for part in (carrier_code, flight_number) if part)
    flight_identifier = combined_identifier or raw.get("url", "").strip("/") or "Unknown"

    return FlightRecord(
        departure_airport=departure_airport,
        departure_time=departure_dt,
        arrival_city=arrival_city,
        arrival_time=arrival_dt,
        airline=airline,
        flight_number=flight_identifier,
        estimated_passengers=None,
    )


def fetch_flightstats_departures(
    *,
    year: int,
    month: int,
    day: int,
    hour: int,
    airport: str,
    session: Optional[_RequestsSession] = None,
    timeout: float = 30.0,
) -> List[FlightRecord]:
    """Return the structured departures list for JFK from FlightStats.

    The FlightStats departures page embeds a Next.js state payload whose
    ``flightTracker.route.flights`` entry holds the planned departures. This
    helper fetches the HTML, extracts the embedded JSON, and returns the data
    as ``FlightRecord`` instances for downstream processing.
    """
    query = DepartureQuery(year=year, month=month, day=day, hour=hour)
    _validate_query(query)
    _target_url = f"{FLIGHTSTATS_DEPARTURES_URL}/{airport}"
    print(_target_url)
    html = _http_get(
        _target_url,
        params=query.as_params(),
        headers=_DEFAULT_HEADERS,
        timeout=timeout,
        session=session,
    )

    payload = _extract_next_data(html)
    flights_payload = _walk_path(payload, _FLIGHTS_PATH)
    if not isinstance(flights_payload, list):
        raise TypeError("Unexpected flights payload returned by FlightStats")
    # print(flights_payload)
    records: List[FlightRecord] = []
    for entry in flights_payload:
        if not isinstance(entry, dict):
            continue
        try:
            _flight_record = _parse_flight_record(entry, departure_airport=airport)
            # print(_flight_record)
            records.append(_flight_record)
        except Exception:
            continue
    return records

@DeprecationWarning
def fetch_flightstats_departures_json(
    *,
    year: int,
    month: int,
    day: int,
    hour: int,
    session: Optional[_RequestsSession] = None,
    timeout: float = 30.0,
) -> str:
    """Return the departures list as a JSON string for downstream parsing."""
    flights = fetch_flightstats_departures(
        year=year,
        month=month,
        day=day,
        hour=hour,
        session=session,
        timeout=timeout,
    )
    return json.dumps([asdict(flight) for flight in flights], ensure_ascii=False)
