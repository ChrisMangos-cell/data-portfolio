import duckdb
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path

DB_PATH = Path("weather_data_pipeline/data/weather_analytics.db")
CHARTS_DIR = Path("weather_data_pipeline/charts")

def generate_temperature_trends():
    con = duckdb.connect(str(DB_PATH), read_only=True)
    df = con.execute("""
        SELECT 
            city_name,
            CAST(observation_timestamp AS TIMESTAMP) AS ts,
            temperature_2m
        FROM stg_weather_observations o
        JOIN dim_locations l USING (location_id)
        ORDER BY ts
    """).df()
    con.close()

    plt.figure(figsize=(12, 6))
    for city in df["city_name"].unique():
        city_data = df[df["city_name"] == city]
        plt.plot(city_data["ts"], city_data["temperature_2m"], label=city, linewidth=1.8)

    plt.title("14-Day Hourly Temperature Trajectory Across Global Metros", fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("Observation Date (UTC)", fontsize=11)
    plt.ylabel("Temperature (°C)", fontsize=11)
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend(loc="upper right", frameon=True)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    plt.tight_layout()
    out_path = CHARTS_DIR / "temperature_trends.png"
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Generated: {out_path}")

def generate_rainfall_comparison():
    con = duckdb.connect(str(DB_PATH), read_only=True)
    df = con.execute("""
        SELECT 
            city_name,
            ROUND(SUM(precipitation_mm), 2) AS total_rain_mm
        FROM stg_weather_observations o
        JOIN dim_locations l USING (location_id)
        GROUP BY city_name
        ORDER BY total_rain_mm DESC
    """).df()
    con.close()

    plt.figure(figsize=(9, 5))
    bars = plt.bar(df["city_name"], df["total_rain_mm"], color="#1f77b4", edgecolor="#0b3c5d", width=0.55)
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 0.3, f"{yval} mm", ha="center", va="bottom", fontweight="bold")

    plt.title("Cumulative 14-Day Precipitation by Metro", fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("City", fontsize=11)
    plt.ylabel("Total Precipitation (mm)", fontsize=11)
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    out_path = CHARTS_DIR / "cumulative_precipitation.png"
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Generated: {out_path}")

if __name__ == "__main__":
    generate_temperature_trends()
    generate_rainfall_comparison()
