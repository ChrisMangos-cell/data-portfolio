import logging
from datetime import datetime, timezone
from typing import Dict, Any
import duckdb
import pandas as pd
import requests

from extract_api import get_resilient_session, LOCATIONS
from transform_load import parse_weather_payload, upsert_observations

logger = logging.getLogger("IncrementalLoader")

def get_watermark(con: duckdb.DuckDBPyConnection, location_id: str) -> datetime:
    """Retrieves the latest ingested observation timestamp for a location."""
    res = con.execute("""
        SELECT MAX(observation_timestamp) 
        FROM stg_weather_observations 
        WHERE location_id = ?
    """, [location_id]).fetchone()[0]
    
    if res is None:
        # Default backfill window if table is empty
        return datetime(2026, 9, 27, 0, 0, 0, tzinfo=timezone.utc)
    
    if res.tzinfo is None:
        return res.replace(tzinfo=timezone.utc)
    return res

def fetch_incremental_weather(
    session: requests.Session, 
    location: Dict[str, Any], 
    watermark: datetime
) -> pd.DataFrame:
    """Extracts only new observations since the watermark timestamp."""
    now = datetime.now(timezone.utc)
    hours_diff = max(1, int((now - watermark).total_seconds() // 3600))
    days_back = min(14, (hours_diff // 24) + 1)
    
    logger.info(f"{location['city']}: Watermark={watermark.strftime('%Y-%m-%d %H:%M UTC')} | Querying past {days_back} day(s)")
    
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": location["lat"],
        "longitude": location["lon"],
        "past_days": days_back,
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
    
    response = session.get(url, params=params, timeout=10)
    response.raise_for_status()
    payload = response.json()
    
    df = parse_weather_payload(payload, location["location_id"])
    
    # Filter strictly for observations newer than the watermark
    df["dt_check"] = pd.to_datetime(df["observation_timestamp"], utc=True)
    df_new = df[df["dt_check"] > watermark].drop(columns=["dt_check"])
    
    return df_new
