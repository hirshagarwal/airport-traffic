from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from fetch.flightstats_fetch import fetch_flightstats_departures
from objects.flight import FlightRecord

__all__ = ["fetch_departures"]

_CACHE_ROOT = Path(__file__).resolve().parent / "cache"


def _ensure_cache_dir() -> None:
    _CACHE_ROOT.mkdir(parents=True, exist_ok=True)


def _cache_file(airport_code: str, year: int, month: int, day: int, hour: int) -> Path:
    sanitized = airport_code.strip().upper() or "UNKNOWN"
    filename = f"{sanitized}_{year:04d}{month:02d}{day:02d}_{hour:02d}.json"
    return _CACHE_ROOT / filename


def _record_to_dict(record: FlightRecord) -> dict:
    return {
        "departure_airport": record.departure_airport,
        "departure_time": record.departure_time.isoformat(),
        "arrival_city": record.arrival_city,
        "arrival_time": record.arrival_time.isoformat(),
        "airline": record.airline,
        "flight_number": record.flight_number,
        "estimated_passengers": record.estimated_passengers,
    }


def _record_from_dict(data: dict) -> FlightRecord:
    return FlightRecord(
        departure_airport=data["departure_airport"],
        departure_time=datetime.fromisoformat(data["departure_time"]),
        arrival_city=data["arrival_city"],
        arrival_time=datetime.fromisoformat(data["arrival_time"]),
        airline=data["airline"],
        flight_number=data["flight_number"],
        estimated_passengers=data.get("estimated_passengers"),
    )


def _load_from_cache(path: Path) -> Optional[List[FlightRecord]]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        if not isinstance(payload, list):
            return None
        records = []
        for item in payload:
            if not isinstance(item, dict):
                continue
            try:
                records.append(_record_from_dict(item))
            except (KeyError, ValueError):
                continue
        return records
    except (OSError, json.JSONDecodeError):
        return None


def _store_to_cache(path: Path, flights: List[FlightRecord]) -> None:
    _ensure_cache_dir()
    serialisable = [_record_to_dict(record) for record in flights]
    with path.open("w", encoding="utf-8") as handle:
        json.dump(serialisable, handle, ensure_ascii=False, indent=2)


def fetch_departures(
    airport_code: str,
    *,
    year: int,
    month: int,
    day: int,
    hour: int,
    use_cache: bool = True,
) -> List[FlightRecord]:
    """Return departures for the requested window, caching results on disk.

    If a cache file already exists for the airport and time window, it is used;
    otherwise the FlightStats service is queried and the response cached for
    future lookups.
    """
    cache_path = _cache_file(airport_code, year, month, day, hour)
    if use_cache and cache_path.exists():
        cached = _load_from_cache(cache_path)
        if cached is not None:
            print("Using cached departures data")
            return cached

    flights = fetch_flightstats_departures(year=year, month=month, day=day, hour=hour, airport=airport_code)
    try:
        _store_to_cache(cache_path, flights)
    except OSError:
        pass
    return flights
