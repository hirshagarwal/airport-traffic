from datetime import datetime
from typing import Dict


def get_tsa_throughput(airport_code: str, dt: datetime) -> Dict[str, int]:
    """Return mocked TSA throughput data for the requested airport and time."""
    baseline = {
        "JFK": 1800,
        "LAX": 2100,
        "SFO": 1500,
        "ORD": 2000,
        "ATL": 2300,
    }
    throughput = baseline.get(airport_code.upper(), 1600)
    return {
        "airport": airport_code.upper(),
        "timestamp": dt.isoformat() + "Z",
        "passengers": throughput,
    }
