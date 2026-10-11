import time
import logging
from typing import Dict, Any, List
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("WeatherExtractor")

# Monitored Locations Configuration
LOCATIONS: List[Dict[str, Any]] = [
    {"location_id": "LOC_MEL", "city": "Melbourne", "country": "Australia", "lat": -37.8136, "lon": 144.9631, "timezone": "Australia/Sydney"},
    {"location_id": "LOC_SYD", "city": "Sydney", "country": "Australia", "lat": -33.8688, "lon": 151.2093, "timezone": "Australia/Sydney"},
    {"location_id": "LOC_LON", "city": "London", "country": "United Kingdom", "lat": 51.5074, "lon": -0.1278, "timezone": "Europe/London"},
    {"location_id": "LOC_NYC", "city": "New York", "country": "United States", "lat": 40.7128, "lon": -74.0060, "timezone": "America/New_York"},
    {"location_id": "LOC_TYO", "city": "Tokyo", "country": "Japan", "lat": 35.6762, "lon": 139.6503, "timezone": "Asia/Tokyo"}
]

def get_resilient_session(retries: int = 5, backoff_factor: float = 1.0) -> requests.Session:
    """Configures a requests Session with automated retry and exponential backoff."""
    session = requests.Session()
    retry_strategy = Retry(
        total=retries,
        backoff_factor=backoff_factor,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
        raise_on_status=False
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session

def fetch_weather_payload(session: requests.Session, location: Dict[str, Any], past_days: int = 14) -> Dict[str, Any]:
    """Extracts raw hourly weather metrics from Open-Meteo API."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": location["lat"],
        "longitude": location["lon"],
        "past_days": past_days,
        "forecast_days": 1,
        "hourly": [
            "temperature_2m",
            "relative_humidity_2m",
            "dew_point_2m",
            "apparent_temperature",
            "precipitation",
            "surface_pressure",
            "wind_speed_10m",
            "wind_direction_10m",
            "cloud_cover"
        ],
        "timezone": "UTC"
    }
    
    logger.info(f"Extracting weather payload for {location['city']} ({location['location_id']})...")
    start = time.time()
    response = session.get(url, params=params, timeout=10)
    duration = time.time() - start
    
    response.raise_for_status()
    payload = response.json()
    logger.info(f"Successfully extracted {location['city']} payload in {duration:.2f}s.")
    return payload
