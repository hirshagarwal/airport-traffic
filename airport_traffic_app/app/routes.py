from datetime import datetime
from typing import List

from flask import Blueprint, jsonify, render_template

from .services.predictor import estimate_traffic

bp = Blueprint("main", __name__)

AIRPORT_CHOICES: List[str] = ["JFK", "LAX", "SFO", "ORD", "ATL"]


@bp.route("/")
def index():
    """Render the landing page with available airport options."""
    return render_template("index.html", airports=AIRPORT_CHOICES)


@bp.route("/estimate/<airport_code>")
def estimate(airport_code: str):
    """Return a mocked passenger load estimate for the given airport."""
    current_time = datetime.utcnow()
    prediction = estimate_traffic(airport_code.upper(), current_time)
    return jsonify(
        {
            "airport": airport_code.upper(),
            "predicted_passenger_load": prediction,
            "generated_at": current_time.isoformat() + "Z",
        }
    )
