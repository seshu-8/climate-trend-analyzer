"""
preprocessor.py
---------------
Handles data loading, cleaning, validation, and feature engineering.
"""

import pandas as pd
import numpy as np


def load_data(filepath: str) -> pd.DataFrame:
    """Load CSV climate data and parse dates."""
    df = pd.read_csv(filepath, parse_dates=["date"])
    print(f"[LOAD] Loaded {df.shape[0]} rows from '{filepath}'")
    return df


def inspect_data(df: pd.DataFrame) -> dict:
    """Print and return basic inspection info."""
    info = {
        "shape": df.shape,
        "dtypes": df.dtypes.to_dict(),
        "null_counts": df.isnull().sum().to_dict(),
        "duplicates": df.duplicated().sum(),
    }
    print("\n=== DATA INSPECTION ===")
    print(f"Shape        : {info['shape']}")
    print(f"Null counts  :\n{df.isnull().sum()}")
    print(f"Duplicates   : {info['duplicates']}")
    print(f"\nSummary Statistics:\n{df.describe().round(2)}")
    return info


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the dataset:
    - Drop duplicate rows
    - Fill or interpolate missing values
    - Clip extreme outliers (temperature, rainfall)
    """
    df = df.drop_duplicates()

    # Interpolate numerical columns if any NaN exists
    num_cols = ["temperature_c", "rainfall_mm", "humidity_pct", "wind_speed_kmh"]
    for col in num_cols:
        if df[col].isnull().any():
            df[col] = df[col].interpolate(method="time")
            print(f"[CLEAN] Interpolated missing values in '{col}'")

    # Clip physical impossibilities
    df["temperature_c"] = df["temperature_c"].clip(-10, 55)
    df["rainfall_mm"] = df["rainfall_mm"].clip(0, 500)
    df["humidity_pct"] = df["humidity_pct"].clip(0, 100)
    df["wind_speed_kmh"] = df["wind_speed_kmh"].clip(0, 200)

    print(f"[CLEAN] Cleaning complete. Final shape: {df.shape}")
    return df


def feature_engineer(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add engineered features:
    - 30-day rolling average temperature
    - 7-day rolling rainfall
    - Year-over-year temperature delta
    - Heat index (simplified)
    """
    df = df.sort_values("date").reset_index(drop=True)

    # Rolling averages
    df["temp_30d_avg"] = df["temperature_c"].rolling(window=30, min_periods=1).mean().round(2)
    df["rain_7d_sum"] = df["rainfall_mm"].rolling(window=7, min_periods=1).sum().round(2)

    # Monthly averages (merged back)
    monthly_avg = df.groupby(["year", "month"])["temperature_c"].mean().reset_index()
    monthly_avg.columns = ["year", "month", "monthly_temp_avg"]
    df = df.merge(monthly_avg, on=["year", "month"], how="left")

    # Simplified heat index: temp + humidity factor
    df["heat_index"] = (df["temperature_c"] + 0.33 * (df["humidity_pct"] / 100 * 6.105) - 4).round(2)

    # Season already present; add quarter
    df["quarter"] = df["date"].dt.quarter

    print("[FEATURE] Feature engineering complete.")
    return df


def get_monthly_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate daily data to monthly summaries."""
    monthly = df.groupby(["year", "month"]).agg(
        avg_temp=("temperature_c", "mean"),
        max_temp=("temperature_c", "max"),
        min_temp=("temperature_c", "min"),
        total_rain=("rainfall_mm", "sum"),
        avg_humidity=("humidity_pct", "mean"),
        avg_wind=("wind_speed_kmh", "mean"),
    ).reset_index()
    monthly["avg_temp"] = monthly["avg_temp"].round(2)
    monthly["total_rain"] = monthly["total_rain"].round(2)
    return monthly


def get_yearly_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate daily data to yearly summaries."""
    yearly = df.groupby("year").agg(
        avg_temp=("temperature_c", "mean"),
        max_temp=("temperature_c", "max"),
        min_temp=("temperature_c", "min"),
        total_rain=("rainfall_mm", "sum"),
        avg_humidity=("humidity_pct", "mean"),
    ).reset_index()
    yearly["avg_temp"] = yearly["avg_temp"].round(2)
    yearly["total_rain"] = yearly["total_rain"].round(2)
    return yearly


if __name__ == "__main__":
    df = load_data("data/climate_data.csv")
    inspect_data(df)
    df = clean_data(df)
    df = feature_engineer(df)
    df.to_csv("data/processed_climate_data.csv", index=False)
    print("\nProcessed data saved.")
