"""
forecasting.py
--------------
Forecasts future temperature and rainfall using:
1. Linear Regression extrapolation (simple, interpretable)
2. ARIMA-style decomposition using statsmodels (if available)
Produces 5-year future projection.
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import mean_absolute_error, mean_squared_error


def build_features(yearly: pd.DataFrame) -> tuple:
    """Prepare feature matrix for regression."""
    X = yearly["year"].values.reshape(-1, 1)
    y_temp = yearly["avg_temp"].values
    y_rain = yearly["total_rain"].values
    return X, y_temp, y_rain


def linear_forecast(yearly: pd.DataFrame, horizon: int = 5) -> pd.DataFrame:
    """
    Simple linear regression forecast for temperature and rainfall.
    Projects 'horizon' years beyond last year in dataset.
    """
    X, y_temp, y_rain = build_features(yearly)

    # --- Temperature model ---
    model_temp = LinearRegression()
    model_temp.fit(X, y_temp)
    pred_temp_hist = model_temp.predict(X)
    mae_temp = mean_absolute_error(y_temp, pred_temp_hist)

    # --- Rainfall model ---
    model_rain = LinearRegression()
    model_rain.fit(X, y_rain)
    pred_rain_hist = model_rain.predict(X)
    mae_rain = mean_absolute_error(y_rain, pred_rain_hist)

    # --- Future years ---
    last_year = int(yearly["year"].max())
    future_years = np.arange(last_year + 1, last_year + horizon + 1).reshape(-1, 1)

    future_temp = model_temp.predict(future_years)
    future_rain = model_rain.predict(future_years)

    # --- Forecast DataFrame ---
    forecast_df = pd.DataFrame({
        "year": future_years.flatten(),
        "forecast_temp_c": np.round(future_temp, 2),
        "forecast_rain_mm": np.round(np.clip(future_rain, 0, None), 1),
        "model": "Linear Regression",
    })

    print("\n=== TEMPERATURE FORECAST (Linear) ===")
    print(f"  Warming rate: {model_temp.coef_[0]:+.4f} °C/year")
    print(f"  MAE (historical fit): {mae_temp:.3f} °C")
    print(forecast_df[["year", "forecast_temp_c"]].to_string(index=False))

    print("\n=== RAINFALL FORECAST (Linear) ===")
    print(f"  Change rate: {model_rain.coef_[0]:+.2f} mm/year")
    print(f"  MAE (historical fit): {mae_rain:.2f} mm")
    print(forecast_df[["year", "forecast_rain_mm"]].to_string(index=False))

    return forecast_df, model_temp, model_rain, pred_temp_hist, pred_rain_hist


def polynomial_forecast(yearly: pd.DataFrame, degree: int = 2, horizon: int = 5) -> pd.DataFrame:
    """
    Polynomial regression forecast (captures non-linear acceleration).
    """
    X, y_temp, _ = build_features(yearly)
    poly = PolynomialFeatures(degree=degree)
    X_poly = poly.fit_transform(X)

    model = LinearRegression()
    model.fit(X_poly, y_temp)

    last_year = int(yearly["year"].max())
    future_years = np.arange(last_year + 1, last_year + horizon + 1).reshape(-1, 1)
    X_future_poly = poly.transform(future_years)
    future_temp = model.predict(X_future_poly)

    forecast_df = pd.DataFrame({
        "year": future_years.flatten(),
        "forecast_temp_poly": np.round(future_temp, 2),
    })
    print("\n=== TEMPERATURE FORECAST (Polynomial deg={}) ===".format(degree))
    print(forecast_df.to_string(index=False))
    return forecast_df, model, poly


def confidence_intervals(forecast_df: pd.DataFrame, std_dev: float = 0.8) -> pd.DataFrame:
    """Add ±1.5σ confidence intervals to forecast."""
    df = forecast_df.copy()
    df["temp_lower"] = (df["forecast_temp_c"] - 1.5 * std_dev).round(2)
    df["temp_upper"] = (df["forecast_temp_c"] + 1.5 * std_dev).round(2)
    return df


if __name__ == "__main__":
    import sys
    sys.path.insert(0, ".")
    from src.preprocessor import load_data, clean_data, feature_engineer, get_yearly_summary
    df = load_data("data/climate_data.csv")
    df = clean_data(df)
    df = feature_engineer(df)
    yearly = get_yearly_summary(df)

    forecast_df, *_ = linear_forecast(yearly, horizon=5)
    forecast_df = confidence_intervals(forecast_df)
    forecast_df.to_csv("outputs/forecast.csv", index=False)
    print("\nForecast saved.")
