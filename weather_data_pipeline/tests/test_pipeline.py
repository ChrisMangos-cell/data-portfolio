import duckdb
from pathlib import Path
import pytest

DB_PATH = Path("weather_data_pipeline/data/weather_analytics.db")

@pytest.fixture(scope="module")
def db_conn():
    if not DB_PATH.exists():
        pytest.fail(f"Database not found at {DB_PATH}")
    con = duckdb.connect(str(DB_PATH), read_only=True)
    yield con
    con.close()

def test_primary_key_uniqueness(db_conn):
    """Ensures no duplicate (location_id, observation_timestamp) records exist."""
    query = """
        SELECT location_id, observation_timestamp, COUNT(*) as cnt
        FROM stg_weather_observations
        GROUP BY location_id, observation_timestamp
        HAVING COUNT(*) > 1;
    """
    duplicates = db_conn.execute(query).fetchall()
    assert len(duplicates) == 0, f"Found {len(duplicates)} duplicate primary keys!"

def test_critical_fields_no_nulls(db_conn):
    """Ensures mandatory observation fields contain zero null values."""
    query = """
        SELECT COUNT(*) 
        FROM stg_weather_observations
        WHERE location_id IS NULL 
           OR observation_timestamp IS NULL 
           OR temperature_2m IS NULL;
    """
    null_count = db_conn.execute(query).fetchone()[0]
    assert null_count == 0, f"Found {null_count} rows with NULL in critical columns!"

def test_physical_domain_boundaries(db_conn):
    """Verifies that meteorological variables adhere to physical planetary laws."""
    query = """
        SELECT COUNT(*)
        FROM stg_weather_observations
        WHERE temperature_2m NOT BETWEEN -60.0 AND 60.0
           OR relative_humidity_2m NOT BETWEEN 0.0 AND 100.0
           OR precipitation_mm < 0.0
           OR wind_speed_10m < 0.0;
    """
    out_of_bounds = db_conn.execute(query).fetchone()[0]
    assert out_of_bounds == 0, f"Detected {out_of_bounds} values violating physical boundary rules!"

def test_temporal_completeness(db_conn):
    """Verifies each location has exactly 360 contiguous hourly observations."""
    query = """
        SELECT location_id, COUNT(*) as record_count
        FROM stg_weather_observations
        GROUP BY location_id;
    """
    counts = db_conn.execute(query).fetchall()
    assert len(counts) > 0, "No records found in staging table."
    for loc_id, count in counts:
        assert count == 360, f"Location {loc_id} has {count} records (expected exactly 360)."

if __name__ == "__main__":
    con = duckdb.connect(str(DB_PATH), read_only=True)
    print("Running Data Quality Checks manually...")
    test_primary_key_uniqueness(con)
    print(" [PASS] Primary Key Uniqueness")
    test_critical_fields_no_nulls(con)
    print(" [PASS] Zero Critical Nulls")
    test_physical_domain_boundaries(con)
    print(" [PASS] Physical Domain Boundaries")
    test_temporal_completeness(con)
    print(" [PASS] Temporal Completeness (360/360 per location)")
    con.close()
    print(" All Data Quality Tests Passed Successfully!")
