-- weather_data_pipeline/sql/01_weather_metrics.sql

-- 1. Daily Aggregated Weather Summary
CREATE OR REPLACE VIEW v_daily_weather_summary AS
SELECT 
    o.location_id,
    l.city_name,
    l.country,
    CAST(o.observation_timestamp AS DATE) AS observation_date,
    ROUND(AVG(o.temperature_2m), 2) AS avg_temp_c,
    ROUND(MIN(o.temperature_2m), 2) AS min_temp_c,
    ROUND(MAX(o.temperature_2m), 2) AS max_temp_c,
    ROUND(MAX(o.temperature_2m) - MIN(o.temperature_2m), 2) AS diurnal_temp_range_c,
    ROUND(AVG(o.relative_humidity_2m), 1) AS avg_humidity_pct,
    ROUND(SUM(o.precipitation_mm), 2) AS total_precipitation_mm,
    ROUND(MAX(o.wind_speed_10m), 2) AS max_wind_speed_kmh,
    ROUND(AVG(o.surface_pressure_hpa), 1) AS avg_pressure_hpa
FROM stg_weather_observations o
JOIN dim_locations l ON o.location_id = l.location_id
GROUP BY 
    o.location_id, 
    l.city_name, 
    l.country, 
    CAST(o.observation_timestamp AS DATE);

-- 2. Rolling Window Metrics (3-Day and 7-Day Moving Averages)
CREATE OR REPLACE VIEW v_rolling_weather_metrics AS
SELECT 
    location_id,
    city_name,
    observation_date,
    avg_temp_c,
    total_precipitation_mm,
    ROUND(AVG(avg_temp_c) OVER (
        PARTITION BY location_id 
        ORDER BY observation_date 
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ), 2) AS rolling_3d_avg_temp_c,
    ROUND(AVG(avg_temp_c) OVER (
        PARTITION BY location_id 
        ORDER BY observation_date 
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ), 2) AS rolling_7d_avg_temp_c,
    ROUND(SUM(total_precipitation_mm) OVER (
        PARTITION BY location_id 
        ORDER BY observation_date 
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ), 2) AS rolling_7d_total_precip_mm
FROM v_daily_weather_summary;
