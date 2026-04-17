"""
app/streamlit_app.py
--------------------
Interactive dashboard for Climate Trend Analyzer.
Run with: streamlit run app/streamlit_app.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from src.data_generator import generate_climate_data
from src.preprocessor import clean_data, feature_engineer, get_monthly_summary, get_yearly_summary
from src.trend_analysis import temperature_trend, rainfall_trend, decade_comparison
from src.anomaly_detection import run_full_anomaly_detection
from src.forecasting import linear_forecast, confidence_intervals

# ── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="🌍 Climate Trend Analyzer",
    page_icon="🌡️",
    layout="wide",
)

# ── Sidebar ──────────────────────────────────────────────────────────────────
st.sidebar.title("⚙️ Settings")
start_year = st.sidebar.slider("Start Year", 1990, 2010, 2000)
end_year = st.sidebar.slider("End Year", 2015, 2024, 2024)
zscore_thresh = st.sidebar.slider("Z-Score Threshold (Anomaly)", 1.5, 4.0, 2.5, 0.1)

# ── Load / Generate Data ─────────────────────────────────────────────────────
@st.cache_data
def load_pipeline(start_year, end_year):
    df = generate_climate_data(start_year=start_year, end_year=end_year)
    df = clean_data(df)
    df = feature_engineer(df)
    monthly = get_monthly_summary(df)
    yearly = get_yearly_summary(df)
    return df, monthly, yearly

df, monthly, yearly = load_pipeline(start_year, end_year)
df, anomaly_table = run_full_anomaly_detection(df)
t_trend = temperature_trend(yearly)
r_trend = rainfall_trend(yearly)
forecast_df, *_ = linear_forecast(yearly, horizon=5)
forecast_df = confidence_intervals(forecast_df)
dec = decade_comparison(yearly)

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🌍 Climate Trend Analyzer")
st.markdown("**Analyzing temperature, rainfall, anomalies, and forecasts for a synthetic climate dataset.**")

# ── KPI Cards ─────────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("📈 Warming Rate", f"{t_trend['slope']:+.3f} °C/year")
col2.metric("🌧️ Rainfall Trend", f"{r_trend['slope']:+.1f} mm/year")
col3.metric("⚠️ Anomaly Days", f"{len(anomaly_table)}")
col4.metric("🔮 2029 Forecast", f"{forecast_df['forecast_temp_c'].iloc[-1]} °C")

st.markdown("---")

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🌡️ Temperature", "🌧️ Rainfall", "⚠️ Anomalies", "🔮 Forecast", "📊 Summary"
])

# Tab 1: Temperature
with tab1:
    st.subheader("Yearly Average Temperature with Trend")
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.bar(yearly["year"], yearly["avg_temp"], color="#E74C3C", alpha=0.7)
    ax.plot(t_trend["years"], t_trend["predicted"], "k--", linewidth=2,
            label=f"Trend: {t_trend['slope']:+.3f}°C/yr")
    ax.legend()
    ax.set_ylabel("Avg Temp (°C)")
    st.pyplot(fig)
    plt.close()

    st.subheader("Monthly Temperature Heatmap")
    pivot = monthly.pivot(index="year", columns="month", values="avg_temp")
    pivot.columns = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    fig2, ax2 = plt.subplots(figsize=(14, 6))
    sns.heatmap(pivot, cmap="RdYlBu_r", ax=ax2, cbar_kws={"label": "°C"})
    st.pyplot(fig2)
    plt.close()

# Tab 2: Rainfall
with tab2:
    st.subheader("Annual Total Rainfall")
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.bar(yearly["year"], yearly["total_rain"], color="#2980B9", alpha=0.8)
    ax.plot(r_trend["years"], r_trend["predicted"], "k--", linewidth=2,
            label=f"Trend: {r_trend['slope']:+.1f} mm/yr")
    ax.legend()
    ax.set_ylabel("Total Rainfall (mm)")
    st.pyplot(fig)
    plt.close()

    st.subheader("Seasonal Rainfall Distribution")
    fig2, ax2 = plt.subplots(figsize=(10, 4))
    season_order = ["Winter", "Summer", "Monsoon", "Post-Monsoon"]
    sns.boxplot(data=df, x="season", y="rainfall_mm", order=season_order, palette="Set1", ax=ax2)
    st.pyplot(fig2)
    plt.close()

# Tab 3: Anomalies
with tab3:
    st.subheader("Detected Climate Anomalies")
    counts = df[df["anomaly_type"] != "Normal"]["anomaly_type"].value_counts()
    col_a, col_b = st.columns([1, 2])
    with col_a:
        st.dataframe(counts.rename("Count").reset_index().rename(columns={"index": "Type"}))
    with col_b:
        fig, ax = plt.subplots(figsize=(8, 4))
        counts.plot(kind="bar", ax=ax, color=["#E74C3C","#2980B9","#8E44AD","#E67E22"], edgecolor="black")
        ax.set_title("Anomaly Counts by Type")
        st.pyplot(fig)
        plt.close()

    st.subheader("Anomaly Table (sample)")
    st.dataframe(anomaly_table.head(50), use_container_width=True)

# Tab 4: Forecast
with tab4:
    st.subheader("5-Year Temperature Forecast")
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(yearly["year"], yearly["avg_temp"], "o-", color="#E74C3C", label="Historical")
    ax.plot(forecast_df["year"], forecast_df["forecast_temp_c"], "s--",
            color="#1ABC9C", linewidth=2, label="Forecast")
    ax.fill_between(forecast_df["year"], forecast_df["temp_lower"],
                    forecast_df["temp_upper"], alpha=0.2, color="#1ABC9C")
    ax.axvline(yearly["year"].max(), color="gray", linestyle=":")
    ax.legend()
    st.pyplot(fig)
    plt.close()
    st.dataframe(forecast_df, use_container_width=True)

# Tab 5: Summary
with tab5:
    st.subheader("Decade Comparison")
    st.dataframe(dec, use_container_width=True)
    st.subheader("Seasonal Trend by Month")
    from src.trend_analysis import seasonal_trend
    s_trend = seasonal_trend(monthly)
    st.dataframe(s_trend, use_container_width=True)

st.markdown("---")
st.caption("Climate Trend Analyzer | Built with Python, Pandas, Matplotlib, Seaborn, Streamlit")
