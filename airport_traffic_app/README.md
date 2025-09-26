# Airport Traffic Estimator

This Flask application demonstrates an MVP for estimating airport traffic using mocked TSA throughput and aircraft movement data. The project is structured so real data sources can be integrated later.

## Getting Started

1. **Create and activate a virtual environment (optional but recommended):**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the development server:**
   ```bash
   flask --app run.py --debug run
   ```
   Or run directly with Python:
   ```bash
   python run.py
   ```
4. **Open the app:**
   Visit http://127.0.0.1:5000/ in your browser.

## Project Layout

```
airport_traffic_app/
├── app/
│   ├── __init__.py
│   ├── routes.py
│   ├── services/
│   │   ├── flights_api.py
│   │   ├── predictor.py
│   │   └── tsa_api.py
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   └── js/
│   │       └── app.js
│   └── templates/
│       └── index.html
├── requirements.txt
├── run.py
├── tests/
│   ├── __init__.py
│   └── test_app.py
└── README.md
```

## Extending the App

- **TSA Integration:** Replace the placeholder in `app/services/tsa_api.py` with real TSA checkpoint throughput requests.
- **Flight Data:** Plug real flight movement data into `app/services/flights_api.py` (e.g., FAA, OpenSky).
- **Prediction Logic:** Enhance `app/services/predictor.py` with statistical or ML models using the real inputs.
- **Frontend Enhancements:** Build richer dashboards or charts in `app/templates/index.html` and supporting JS/CSS.

## Running Tests

Execute the test suite with:
```bash
pytest
```
