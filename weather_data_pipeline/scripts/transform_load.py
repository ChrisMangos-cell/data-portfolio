import duckdb
import pandas as pd
import logging
from typing import Dict, Any, List
from pathlib import Path

logger = logging.getLogger("WeatherLoader")

def parse_weather_payload(payload: Dict[str, Any], location_id: str) -> pd.DataFrame:
    """Normalizes nested API JSON arrays into a flat, typed DataFrame."""
    hourly_data = payload.get("hourly", {})
    if not hourly_data or "time" not in hourly_data:
        raise ValueError("Payload missing 'hourly' metrics array.")
        
    df = pd.DataFrame({
        "location_id": location_id,
        "observation_timestamp": pd.to_datetime(hourly_data["time"], utc=True),
        "temperature_2m": hourly_data.get("temperature_2m"),
        "relative_humidity_2m": hourly_data.get("relative_humidity_2m"),
        "dew_point_2m": hourly_data.get("dew_point_2m"),
        "apparent_temperature": hourly_data.get("apparent_temperature"),
        "precipitation_mm": hourly_data.get("precipitation"),
        "surface_pressure_hpa": hourly_data.get("surface_pressure"),
        "wind_speed_10m": hourly_data.get("wind_speed_10m"),
        "wind_direction_10m": hourly_data.get("wind_direction_10m"),
        "cloud_cover_pct": hourly_data.get("cloud_cover")
    })
    
    df["observation_timestamp"] = df["observation_timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
    return df

def init_database(db_path: Path, ddl_path: Path) -> duckdb.DuckDBPyConnection:
    """Initializes DuckDB database and executes staging DDL."""
    con = duckdb.connect(str(db_path))
    con.execute(ddl_path.read_text())
    return con

def sync_locations_dim(con: duckdb.DuckDBPyConnection, locations: List[Dict[str, Any]]):
    """Upserts metadata records into dim_locations."""
    loc_df = pd.DataFrame([{
        "location_id": l["location_id"],
        "city_name": l["city"],
        "country": l["country"],
        "latitude": l["lat"],
        "longitude": l["lon"],
        "timezone": l["timezone"],
        "is_active": True
    } for l in locations])
    
    con.register("tmp_locs", loc_df)
    con.execute("""
        INSERT OR REPLACE INTO dim_locations 
        SELECT location_id, city_name, country, latitude, longitude, timezone, is_active, CURRENT_TIMESTAMP 
        FROM tmp_locs;
    """)
    con.unregister("tmp_locs")

def upsert_observations(con: duckdb.DuckDBPyConnection, df: pd.DataFrame):
    """Performs an idempotent upsert into stg_weather_observations."""
    con.register("tmp_obs", df)
    con.execute("""
        INSERT OR REPLACE INTO stg_weather_observations (
            location_id,
            observation_timestamp,
            temperature_2m,
            relative_humidity_2m,
            dew_point_2m,
            apparent_temperature,
            precipitation_mm,
            surface_pressure_hpa,
            wind_speed_10m,
            wind_direction_10m,
            cloud_cover_pct
        )
        SELECT 
            location_id,
            observation_timestamp::TIMESTAMP,
            temperature_2m,
            relative_humidity_2m,
            dew_point_2m,
            apparent_temperature,
            precipitation_mm,
            surface_pressure_hpa,
            wind_speed_10m,
            wind_direction_10m,
            cloud_cover_pct
        FROM tmp_obs;
    """)
    con.unregister("tmp_obs")
