"""
trend_analysis.py
-----------------
Computes climate trends:
- Linear regression on yearly avg temperature (warming rate)
- Rainfall trend over years
- Seasonal shift detection
- Mann-Kendall trend test (via scipy)
"""

import numpy as np
import pandas as pd
from scipy import stats


def linear_trend(x: np.ndarray, y: np.ndarray) -> dict:
    """
    Fit a linear trend (OLS) to data.
    Returns slope, intercept, R², p-value.
    """
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    return {
        "slope": round(slope, 4),
        "intercept": round(intercept, 4),
        "r_squared": round(r_value ** 2, 4),
        "p_value": round(p_value, 6),
        "std_err": round(std_err, 6),
        "significant": p_value < 0.05,
    }


def temperature_trend(yearly: pd.DataFrame) -> dict:
    """
    Compute warming trend from yearly average temperatures.
    Returns trend stats and predicted values.
    """
    x = yearly["year"].values
    y = yearly["avg_temp"].values
    trend = linear_trend(x, y)
    trend["predicted"] = trend["slope"] * x + trend["intercept"]
    trend["years"] = x.tolist()
    print("\n=== TEMPERATURE TREND ===")
    print(f"  Warming Rate : {trend['slope']:+.4f} °C/year")
    print(f"  R²           : {trend['r_squared']}")
    print(f"  Significant  : {trend['significant']} (p={trend['p_value']})")
    return trend


def rainfall_trend(yearly: pd.DataFrame) -> dict:
    """Compute trend in annual total rainfall."""
    x = yearly["year"].values
    y = yearly["total_rain"].values
    trend = linear_trend(x, y)
    trend["predicted"] = trend["slope"] * x + trend["intercept"]
    trend["years"] = x.tolist()
    print("\n=== RAINFALL TREND ===")
    print(f"  Change Rate  : {trend['slope']:+.2f} mm/year")
    print(f"  Significant  : {trend['significant']} (p={trend['p_value']})")
    return trend


def seasonal_trend(monthly: pd.DataFrame) -> pd.DataFrame:
    """
    For each calendar month, compute temperature trend over years.
    Helps detect if summers are getting hotter, winters milder, etc.
    """
    results = []
    for m in range(1, 13):
        subset = monthly[monthly["month"] == m]
        if len(subset) < 5:
            continue
        x = subset["year"].values
        y = subset["avg_temp"].values
        t = linear_trend(x, y)
        results.append({
            "month": m,
            "slope_c_per_year": t["slope"],
            "r_squared": t["r_squared"],
            "significant": t["significant"],
        })
    df_seasonal = pd.DataFrame(results)
    print("\n=== SEASONAL TEMPERATURE TRENDS ===")
    print(df_seasonal.to_string(index=False))
    return df_seasonal


def decade_comparison(yearly: pd.DataFrame) -> pd.DataFrame:
    """Compare average temperature across decades."""
    yearly = yearly.copy()
    yearly["decade"] = (yearly["year"] // 10) * 10
    dec = yearly.groupby("decade").agg(
        avg_temp=("avg_temp", "mean"),
        total_rain=("total_rain", "mean"),
    ).reset_index()
    dec["avg_temp"] = dec["avg_temp"].round(2)
    dec["total_rain"] = dec["total_rain"].round(2)
    print("\n=== DECADE COMPARISON ===")
    print(dec.to_string(index=False))
    return dec


if __name__ == "__main__":
    from preprocessor import load_data, clean_data, feature_engineer, get_yearly_summary, get_monthly_summary
    df = load_data("data/climate_data.csv")
    df = clean_data(df)
    df = feature_engineer(df)
    yearly = get_yearly_summary(df)
    monthly = get_monthly_summary(df)

    t_trend = temperature_trend(yearly)
    r_trend = rainfall_trend(yearly)
    s_trend = seasonal_trend(monthly)
    dec = decade_comparison(yearly)
