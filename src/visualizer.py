"""
visualizer.py
-------------
All chart/plot generation for Climate Trend Analyzer.
Saves PNG files to outputs/images/ and displays inline in notebooks.
"""

import matplotlib
matplotlib.use("Agg")  # non-interactive backend for scripts
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import pandas as pd
import numpy as np
import os

# Style
sns.set_theme(style="darkgrid", palette="husl")
SAVE_DIR = "outputs/images"
os.makedirs(SAVE_DIR, exist_ok=True)

COLORS = {
    "temp": "#E74C3C",
    "rain": "#2980B9",
    "humidity": "#27AE60",
    "wind": "#8E44AD",
    "trend": "#F39C12",
    "anomaly": "#C0392B",
    "forecast": "#1ABC9C",
}


def save_fig(fig, name: str):
    path = os.path.join(SAVE_DIR, f"{name}.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"[SAVED] {path}")


# ── 1. Temperature over time ────────────────────────────────────────────────
def plot_temperature_timeseries(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(df["date"], df["temperature_c"], color=COLORS["temp"], alpha=0.4, linewidth=0.6, label="Daily Temp")
    ax.plot(df["date"], df["temp_30d_avg"], color="black", linewidth=1.4, label="30-Day Rolling Avg")
    ax.set_title("Daily Temperature with 30-Day Rolling Average (2000–2024)", fontsize=14, fontweight="bold")
    ax.set_xlabel("Date")
    ax.set_ylabel("Temperature (°C)")
    ax.legend()
    save_fig(fig, "01_temperature_timeseries")


# ── 2. Yearly average temperature + trend line ──────────────────────────────
def plot_yearly_temp_trend(yearly: pd.DataFrame, t_trend: dict):
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.bar(yearly["year"], yearly["avg_temp"], color=COLORS["temp"], alpha=0.7, label="Yearly Avg Temp")
    ax.plot(t_trend["years"], t_trend["predicted"], color=COLORS["trend"], linewidth=2.5,
            linestyle="--", label=f"Trend (+{t_trend['slope']:+.3f}°C/yr)")
    ax.set_title("Yearly Average Temperature with Warming Trend", fontsize=14, fontweight="bold")
    ax.set_xlabel("Year")
    ax.set_ylabel("Avg Temperature (°C)")
    ax.legend()
    save_fig(fig, "02_yearly_temp_trend")


# ── 3. Rainfall over years ───────────────────────────────────────────────────
def plot_yearly_rainfall(yearly: pd.DataFrame, r_trend: dict):
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.bar(yearly["year"], yearly["total_rain"], color=COLORS["rain"], alpha=0.8, label="Annual Rainfall")
    ax.plot(r_trend["years"], r_trend["predicted"], color=COLORS["trend"],
            linewidth=2.5, linestyle="--", label=f"Trend ({r_trend['slope']:+.1f} mm/yr)")
    ax.set_title("Annual Total Rainfall with Trend", fontsize=14, fontweight="bold")
    ax.set_xlabel("Year")
    ax.set_ylabel("Rainfall (mm)")
    ax.legend()
    save_fig(fig, "03_yearly_rainfall_trend")


# ── 4. Seasonal box plots ────────────────────────────────────────────────────
def plot_seasonal_boxplot(df: pd.DataFrame):
    season_order = ["Winter", "Summer", "Monsoon", "Post-Monsoon"]
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    sns.boxplot(data=df, x="season", y="temperature_c", order=season_order,
                palette="Set2", ax=axes[0])
    axes[0].set_title("Temperature by Season", fontweight="bold")
    axes[0].set_ylabel("Temperature (°C)")

    sns.boxplot(data=df, x="season", y="rainfall_mm", order=season_order,
                palette="Set1", ax=axes[1])
    axes[1].set_title("Rainfall by Season", fontweight="bold")
    axes[1].set_ylabel("Rainfall (mm)")

    fig.suptitle("Seasonal Climate Distribution", fontsize=14, fontweight="bold")
    plt.tight_layout()
    save_fig(fig, "04_seasonal_boxplots")


# ── 5. Monthly heatmap ───────────────────────────────────────────────────────
def plot_monthly_heatmap(monthly: pd.DataFrame):
    pivot = monthly.pivot(index="year", columns="month", values="avg_temp")
    pivot.columns = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

    fig, ax = plt.subplots(figsize=(14, 8))
    sns.heatmap(pivot, cmap="RdYlBu_r", annot=False, linewidths=0.3,
                cbar_kws={"label": "Avg Temperature (°C)"}, ax=ax)
    ax.set_title("Monthly Average Temperature Heatmap (2000–2024)", fontsize=14, fontweight="bold")
    ax.set_xlabel("Month")
    ax.set_ylabel("Year")
    save_fig(fig, "05_monthly_temp_heatmap")


# ── 6. Anomaly scatter plot ──────────────────────────────────────────────────
def plot_anomalies(df: pd.DataFrame):
    colors = {
        "Normal": "#BDC3C7",
        "Heatwave": "#E74C3C",
        "Cold Snap": "#2980B9",
        "Heavy Rainfall": "#8E44AD",
        "Drought": "#E67E22",
    }
    fig, ax = plt.subplots(figsize=(14, 5))

    for atype, color in colors.items():
        subset = df[df["anomaly_type"] == atype]
        alpha = 0.15 if atype == "Normal" else 0.9
        size = 2 if atype == "Normal" else 20
        ax.scatter(subset["date"], subset["temperature_c"],
                   color=color, alpha=alpha, s=size, label=atype)

    ax.set_title("Climate Anomalies: Temperature with Event Labels", fontsize=14, fontweight="bold")
    ax.set_xlabel("Date")
    ax.set_ylabel("Temperature (°C)")
    ax.legend(markerscale=3)
    save_fig(fig, "06_anomaly_scatter")


# ── 7. Anomaly type bar chart ────────────────────────────────────────────────
def plot_anomaly_counts(df: pd.DataFrame):
    counts = df[df["anomaly_type"] != "Normal"]["anomaly_type"].value_counts()
    fig, ax = plt.subplots(figsize=(8, 5))
    counts.plot(kind="bar", color=[COLORS["anomaly"], COLORS["rain"], COLORS["wind"], COLORS["temp"]],
                ax=ax, edgecolor="black")
    ax.set_title("Anomaly Event Counts by Type", fontsize=14, fontweight="bold")
    ax.set_xlabel("Anomaly Type")
    ax.set_ylabel("Number of Days")
    ax.tick_params(axis="x", rotation=30)
    save_fig(fig, "07_anomaly_counts")


# ── 8. Forecast plot ─────────────────────────────────────────────────────────
def plot_forecast(yearly: pd.DataFrame, forecast_df: pd.DataFrame):
    forecast_df = forecast_df.copy()
    if "temp_lower" not in forecast_df.columns:
        forecast_df["temp_lower"] = forecast_df["forecast_temp_c"] - 1.2
        forecast_df["temp_upper"] = forecast_df["forecast_temp_c"] + 1.2

    fig, ax = plt.subplots(figsize=(13, 5))
    ax.plot(yearly["year"], yearly["avg_temp"], color=COLORS["temp"],
            marker="o", markersize=4, linewidth=1.5, label="Historical")
    ax.plot(forecast_df["year"], forecast_df["forecast_temp_c"],
            color=COLORS["forecast"], marker="s", markersize=6,
            linewidth=2, linestyle="--", label="Forecast")
    ax.fill_between(forecast_df["year"],
                    forecast_df["temp_lower"], forecast_df["temp_upper"],
                    alpha=0.2, color=COLORS["forecast"], label="95% CI")
    ax.axvline(x=yearly["year"].max(), color="gray", linestyle=":", linewidth=1.5)
    ax.set_title("Temperature Forecast: Next 5 Years", fontsize=14, fontweight="bold")
    ax.set_xlabel("Year")
    ax.set_ylabel("Avg Temperature (°C)")
    ax.legend()
    save_fig(fig, "08_temperature_forecast")


# ── 9. Correlation heatmap ───────────────────────────────────────────────────
def plot_correlation_heatmap(df: pd.DataFrame):
    cols = ["temperature_c", "rainfall_mm", "humidity_pct", "wind_speed_kmh", "heat_index"]
    corr = df[cols].corr()
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm",
                linewidths=0.5, ax=ax, cbar_kws={"shrink": 0.8})
    ax.set_title("Climate Variable Correlation Matrix", fontsize=13, fontweight="bold")
    save_fig(fig, "09_correlation_heatmap")


# ── 10. Decade comparison bar ────────────────────────────────────────────────
def plot_decade_comparison(dec: pd.DataFrame):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    axes[0].bar(dec["decade"].astype(str), dec["avg_temp"], color=COLORS["temp"], edgecolor="black")
    axes[0].set_title("Avg Temperature by Decade", fontweight="bold")
    axes[0].set_ylabel("°C")

    axes[1].bar(dec["decade"].astype(str), dec["total_rain"], color=COLORS["rain"], edgecolor="black")
    axes[1].set_title("Avg Annual Rainfall by Decade", fontweight="bold")
    axes[1].set_ylabel("mm")

    fig.suptitle("Decade-wise Climate Comparison", fontsize=14, fontweight="bold")
    plt.tight_layout()
    save_fig(fig, "10_decade_comparison")


def generate_all_plots(df, yearly, monthly, t_trend, r_trend, forecast_df, dec):
    """Run all visualizations in one call."""
    print("\n=== GENERATING ALL PLOTS ===")
    plot_temperature_timeseries(df)
    plot_yearly_temp_trend(yearly, t_trend)
    plot_yearly_rainfall(yearly, r_trend)
    plot_seasonal_boxplot(df)
    plot_monthly_heatmap(monthly)
    plot_anomalies(df)
    plot_anomaly_counts(df)
    plot_forecast(yearly, forecast_df)
    plot_correlation_heatmap(df)
    plot_decade_comparison(dec)
    print("[DONE] All 10 plots saved to outputs/images/")
