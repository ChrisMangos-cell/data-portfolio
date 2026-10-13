import duckdb
import pandas as pd
from pathlib import Path

DB_PATH = Path("weather_data_pipeline/data/weather_analytics.db")

def detect_weather_anomalies(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    """
    Identifies meteorological anomalies using windowed Z-score calculations
    and threshold filters for extreme wind and rainfall.
    """
    query = """
    WITH base_stats AS (
        SELECT 
            location_id,
            city_name,
            observation_timestamp,
            temperature_2m,
            precipitation_mm,
            wind_speed_10m,
            AVG(temperature_2m) OVER(PARTITION BY location_id) AS temp_mean,
            STDDEV(temperature_2m) OVER(PARTITION BY location_id) AS temp_stddev,
            AVG(wind_speed_10m) OVER(PARTITION BY location_id) AS wind_mean,
            STDDEV(wind_speed_10m) OVER(PARTITION BY location_id) AS wind_stddev
        FROM stg_weather_observations o
        JOIN dim_locations l USING (location_id)
    ),
    z_scores AS (
        SELECT 
            location_id,
            city_name,
            observation_timestamp,
            temperature_2m,
            precipitation_mm,
            wind_speed_10m,
            ROUND((temperature_2m - temp_mean) / NULLIF(temp_stddev, 0), 2) AS temp_zscore,
            ROUND((wind_speed_10m - wind_mean) / NULLIF(wind_stddev, 0), 2) AS wind_zscore
        FROM base_stats
    )
    SELECT 
        city_name,
        observation_timestamp,
        temperature_2m,
        temp_zscore,
        precipitation_mm,
        wind_speed_10m,
        wind_zscore,
        CASE 
            WHEN temp_zscore >= 2.5 THEN 'Extreme Heat Anomaly'
            WHEN temp_zscore <= -2.5 THEN 'Extreme Cold Anomaly'
            WHEN precipitation_mm >= 5.0 THEN 'Flash Precipitation'
            WHEN wind_zscore >= 2.5 THEN 'Gale Force Wind Gust'
            ELSE 'Normal'
        END AS anomaly_classification
    FROM z_scores
    WHERE ABS(temp_zscore) >= 2.5 
       OR precipitation_mm >= 5.0 
       OR wind_zscore >= 2.5
    ORDER BY observation_timestamp DESC;
    """
    return con.execute(query).df()

if __name__ == "__main__":
    con = duckdb.connect(str(DB_PATH), read_only=True)
    df_anomalies = detect_weather_anomalies(con)
    print(f"\n==========================================")
    print(f"TOTAL METEOROLOGICAL ANOMALIES FLAGGED: {len(df_anomalies)}")
    print(f"==========================================\n")
    if not df_anomalies.empty:
        print(df_anomalies.head(15).to_string(index=False))
    else:
        print("No extreme deviations (|Z| >= 2.5 or rain >= 5mm) detected in current observation window.")
    con.close()
