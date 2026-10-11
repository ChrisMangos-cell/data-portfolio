-- weather_data_pipeline/sql/00_staging_ddl.sql

-- 1. Dimension Table: Monitored Locations
CREATE TABLE IF NOT EXISTS dim_locations (
    location_id VARCHAR PRIMARY KEY,
    city_name VARCHAR NOT NULL,
    country VARCHAR NOT NULL,
    latitude DOUBLE NOT NULL,
    longitude DOUBLE NOT NULL,
    timezone VARCHAR NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Staging Table: Hourly Raw Weather Observations
-- Composite Primary Key guarantees idempotency
CREATE TABLE IF NOT EXISTS stg_weather_observations (
    location_id VARCHAR NOT NULL,
    observation_timestamp TIMESTAMP NOT NULL,
    temperature_2m DOUBLE,
    relative_humidity_2m DOUBLE,
    dew_point_2m DOUBLE,
    apparent_temperature DOUBLE,
    precipitation_mm DOUBLE,
    surface_pressure_hpa DOUBLE,
    wind_speed_10m DOUBLE,
    wind_direction_10m DOUBLE,
    cloud_cover_pct DOUBLE,
    ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (location_id, observation_timestamp),
    FOREIGN KEY (location_id) REFERENCES dim_locations (location_id)
);

-- 3. Optimization Indexes for analytical slicing
CREATE INDEX IF NOT EXISTS idx_obs_time ON stg_weather_observations (observation_timestamp);
CREATE INDEX IF NOT EXISTS idx_obs_loc_time ON stg_weather_observations (location_id, observation_timestamp);
