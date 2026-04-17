"""
data_generator.py
-----------------
Generates synthetic but realistic climate dataset.
Simulates temperature, rainfall, humidity, and wind speed
with seasonal patterns, long-term warming trend, and anomalies.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_climate_data(start_year=2000, end_year=2024, seed=42):
    """
    Generate a synthetic climate dataset from start_year to end_year.
    Includes:
      - Daily temperature (°C) with seasonal cycles + warming trend + noise
      - Rainfall (mm) with seasonal patterns
      - Humidity (%)
      - Wind speed (km/h)
      - Injected anomalies (heatwaves, drought months)
    """
    np.random.seed(seed)

    # --- Date range ---
    dates = pd.date_range(start=f"{start_year}-01-01", end=f"{end_year}-12-31", freq="D")
    n = len(dates)

    day_of_year = np.array([d.timetuple().tm_yday for d in dates])
    year_fraction = np.array([(d.year - start_year) for d in dates])  # 0, 1, 2, ...

    # --- Temperature ---
    # Base seasonal cycle (India-like: hot summers, mild winters)
    seasonal_temp = 27 + 10 * np.sin(2 * np.pi * (day_of_year - 80) / 365)
    # Long-term warming trend: +0.025°C per year
    warming_trend = 0.025 * year_fraction
    # Random daily noise
    noise_temp = np.random.normal(0, 1.5, n)
    temperature = seasonal_temp + warming_trend + noise_temp

    # --- Rainfall ---
    # Monsoon peaks around day 180-270 (July–Sep)
    seasonal_rain = np.maximum(0,
        8 * np.sin(2 * np.pi * (day_of_year - 150) / 365) +
        np.random.exponential(2, n)
    )
    # Dry months get near-zero rainfall
    seasonal_rain[day_of_year < 100] *= 0.1
    seasonal_rain[day_of_year > 300] *= 0.15
    rainfall = np.clip(seasonal_rain, 0, 200)

    # --- Humidity ---
    humidity = 60 + 20 * np.sin(2 * np.pi * (day_of_year - 180) / 365) + \
               np.random.normal(0, 5, n)
    humidity = np.clip(humidity, 20, 100)

    # --- Wind speed ---
    wind_speed = 15 + 5 * np.sin(2 * np.pi * (day_of_year - 60) / 365) + \
                 np.random.normal(0, 3, n)
    wind_speed = np.clip(wind_speed, 0, 80)

    # --- Inject anomalies ---
    # Heatwave: 10-day spike in May 2010
    hw_mask = (dates >= "2010-05-15") & (dates <= "2010-05-25")
    temperature[hw_mask] += np.random.uniform(6, 10, hw_mask.sum())

    # Cold snap: 7-day dip in Dec 2015
    cs_mask = (dates >= "2015-12-10") & (dates <= "2015-12-17")
    temperature[cs_mask] -= np.random.uniform(5, 8, cs_mask.sum())

    # Drought: low rainfall in July 2018
    dr_mask = (dates >= "2018-07-01") & (dates <= "2018-07-31")
    rainfall[dr_mask] *= 0.05

    # Flood month: heavy rainfall in Aug 2022
    fl_mask = (dates >= "2022-08-01") & (dates <= "2022-08-15")
    rainfall[fl_mask] += np.random.uniform(80, 150, fl_mask.sum())

    # --- Build DataFrame ---
    df = pd.DataFrame({
        "date": dates,
        "temperature_c": np.round(temperature, 2),
        "rainfall_mm": np.round(rainfall, 2),
        "humidity_pct": np.round(humidity, 1),
        "wind_speed_kmh": np.round(wind_speed, 1),
    })

    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["day"] = df["date"].dt.day
    df["season"] = df["month"].map({
        12: "Winter", 1: "Winter", 2: "Winter",
        3: "Summer", 4: "Summer", 5: "Summer",
        6: "Monsoon", 7: "Monsoon", 8: "Monsoon",
        9: "Post-Monsoon", 10: "Post-Monsoon", 11: "Post-Monsoon"
    })

    return df


if __name__ == "__main__":
    df = generate_climate_data()
    df.to_csv("data/climate_data.csv", index=False)
    print(f"Dataset generated: {df.shape[0]} rows, {df.shape[1]} columns")
    print(df.head())
