import sys
import logging
from pathlib import Path
import duckdb

# Configure dual logging (terminal + disk log file)
LOG_FILE = Path("weather_data_pipeline/logs/pipeline.log")
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8")
    ]
)
logger = logging.getLogger("WeatherPipelineMaster")

# Add scripts directory to module path
sys.path.append(str(Path("weather_data_pipeline/scripts").resolve()))
sys.path.append(str(Path("weather_data_pipeline/tests").resolve()))

from extract_api import get_resilient_session, fetch_weather_payload, LOCATIONS
from transform_load import init_database, sync_locations_dim, parse_weather_payload, upsert_observations
from test_pipeline import (
    test_primary_key_uniqueness, 
    test_critical_fields_no_nulls, 
    test_physical_domain_boundaries, 
    test_temporal_completeness
)

def run():
    logger.info("==================================================")
    logger.info("  STARTING WEATHER DATA PIPELINE EXECUTION        ")
    logger.info("==================================================")
    
    db_path = Path("weather_data_pipeline/data/weather_analytics.db")
    ddl_path = Path("weather_data_pipeline/sql/00_staging_ddl.sql")
    metrics_path = Path("weather_data_pipeline/sql/01_weather_metrics.sql")
    
    # 1. Initialize DB & Staging DDL
    logger.info("Step 1: Connecting to DuckDB & ensuring staging DDL...")
    con = init_database(db_path, ddl_path)
    
    # 2. Sync Location Dimensions
    logger.info("Step 2: Syncing dimension records for monitored cities...")
    sync_locations_dim(con, LOCATIONS)
    
    # 3. Extract & Upsert Observations
    logger.info("Step 3: Extracting weather observations from Open-Meteo REST API...")
    session = get_resilient_session(retries=5, backoff_factor=1.0)
    total_loaded = 0
    
    for loc in LOCATIONS:
        try:
            payload = fetch_weather_payload(session, loc, past_days=14)
            clean_df = parse_weather_payload(payload, loc["location_id"])
            upsert_observations(con, clean_df)
            total_loaded += len(clean_df)
            logger.info(f"   -> Staged {len(clean_df)} observations for {loc['city']}, {loc['country']}")
        except Exception as e:
            logger.error(f"Failed pipeline run for {loc['city']}: {e}", exc_info=True)
            raise
            
    logger.info(f"Ingestion complete: {total_loaded:,} observations processed.")
    
    # 4. Instantiate Analytical Views
    logger.info("Step 4: Executing analytical rollup and window metric SQL views...")
    con.execute(metrics_path.read_text())
    
    # 5. Run Automated Data Quality Assertions
    logger.info("Step 5: Running pipeline validation assertions...")
    test_primary_key_uniqueness(con)
    test_critical_fields_no_nulls(con)
    test_physical_domain_boundaries(con)
    test_temporal_completeness(con)
    logger.info("All data quality tests passed with 0 errors.")
    
    # 6. Preview Analytical Output
    logger.info("Step 6: Pipeline output preview (v_rolling_weather_metrics):")
    preview = con.execute("""
        SELECT city_name, observation_date, avg_temp_c, rolling_7d_avg_temp_c, rolling_7d_total_precip_mm
        FROM v_rolling_weather_metrics
        WHERE observation_date = (SELECT MAX(observation_date) FROM v_rolling_weather_metrics)
        ORDER BY city_name;
    """).df()
    
    con.close()
    
    print("\n" + preview.to_string(index=False) + "\n")
    logger.info("==================================================")
    logger.info("  WEATHER DATA PIPELINE COMPLETED SUCCESSFULLY    ")
    logger.info("==================================================")

if __name__ == "__main__":
    run()
