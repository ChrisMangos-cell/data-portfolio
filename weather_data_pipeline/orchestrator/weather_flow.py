import sys
import logging
from pathlib import Path
from prefect import task, flow
import duckdb

# Path setup
sys.path.append(str(Path("weather_data_pipeline/scripts").resolve()))
sys.path.append(str(Path("weather_data_pipeline/tests").resolve()))

from extract_api import get_resilient_session, LOCATIONS
from transform_load import init_database, sync_locations_dim, upsert_observations
from incremental_loader import get_watermark, fetch_incremental_weather
from test_pipeline import (
    test_primary_key_uniqueness, 
    test_critical_fields_no_nulls, 
    test_physical_domain_boundaries
)

DB_PATH = Path("weather_data_pipeline/data/weather_analytics.db")
DDL_PATH = Path("weather_data_pipeline/sql/00_staging_ddl.sql")
METRICS_PATH = Path("weather_data_pipeline/sql/01_weather_metrics.sql")

@task(name="initialize-storage", retries=2, retry_delay_seconds=5)
def task_init_storage():
    """Initializes DuckDB staging schema and verifies dimension tables."""
    con = init_database(DB_PATH, DDL_PATH)
    sync_locations_dim(con, LOCATIONS)
    con.close()
    return True

@task(name="extract-incremental-city", retries=3, retry_delay_seconds=10)
def task_extract_city(loc: dict):
    """Checks the watermark and fetches incremental payloads for a single city."""
    con = duckdb.connect(str(DB_PATH))
    session = get_resilient_session()
    
    watermark = get_watermark(con, loc["location_id"])
    df_new = fetch_incremental_weather(session, loc, watermark)
    
    rows_added = 0
    if not df_new.empty:
        upsert_observations(con, df_new)
        rows_added = len(df_new)
        
    con.close()
    return {"city": loc["city"], "watermark": str(watermark), "new_rows": rows_added}

@task(name="refresh-analytical-views")
def task_refresh_views():
    """Recalculates rolling aggregations and metrics views."""
    con = duckdb.connect(str(DB_PATH))
    con.execute(METRICS_PATH.read_text())
    con.close()

@task(name="data-quality-guardrails")
def task_run_assertions():
    """Asserts data quality invariants across primary keys and physical limits."""
    con = duckdb.connect(str(DB_PATH), read_only=True)
    test_primary_key_uniqueness(con)
    test_critical_fields_no_nulls(con)
    test_physical_domain_boundaries(con)
    con.close()
    return "All checks passed"

@flow(name="daily-weather-ingestion-pipeline")
def weather_pipeline_flow():
    """Master workflow orchestrating incremental extraction, loading, and assertions."""
    # Step 1: Storage verification
    task_init_storage()
    
    # Step 2: Incremental extractions (parallelizable tasks)
    results = []
    for loc in LOCATIONS:
        res = task_extract_city(loc)
        results.append(res)
    
    # Step 3: Analytical refresh
    task_refresh_views()
    
    # Step 4: Quality assertions
    task_run_assertions()
    
    return results

if __name__ == "__main__":
    weather_pipeline_flow()
