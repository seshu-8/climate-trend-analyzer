# Climate Trend Analyzer — Architecture

## System Architecture (Text Block Diagram)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CLIMATE TREND ANALYZER PIPELINE                  │
└─────────────────────────────────────────────────────────────────────┘

  ┌──────────────────┐
  │  DATA SOURCE      │   ← Synthetic CSV (simulate real gov/NASA data)
  │  climate_data.csv │
  └────────┬─────────┘
           │
           ▼
  ┌──────────────────────┐
  │  PREPROCESSOR         │
  │  - Load & inspect     │
  │  - Clean (clip, fill) │
  │  - Feature engineer   │   → processed_climate_data.csv
  │  - Monthly/Yearly agg │   → monthly_summary.csv
  └────────┬─────────────┘   → yearly_summary.csv
           │
     ┌─────┴──────┐
     ▼            ▼
┌─────────────┐  ┌──────────────────┐
│ TREND        │  │ ANOMALY DETECTION │
│ ANALYSIS     │  │ - Z-Score         │
│ - Warming    │  │ - IQR             │
│   rate       │  │ - Rolling window  │
│ - Rainfall   │  │ - Event labeling  │
│   trend      │  └──────────────────┘
│ - Seasonal   │
│ - Decade     │
└──────┬──────┘
       │
       ▼
  ┌──────────────────┐
  │  FORECASTING      │
  │  - Linear Regress │
  │  - Polynomial     │
  │  - 5-yr outlook   │   → forecast.csv
  └────────┬─────────┘
           │
           ▼
  ┌──────────────────────────┐
  │  VISUALIZER               │
  │  10 charts generated:     │
  │  - Time series            │
  │  - Trend bars             │
  │  - Seasonal boxes         │
  │  - Monthly heatmap        │
  │  - Anomaly scatter        │
  │  - Forecast + CI          │
  │  - Correlation matrix     │
  │  - Decade comparison      │
  └────────┬─────────────────┘
           │
           ▼
  ┌──────────────────────────┐
  │  OUTPUTS                  │
  │  outputs/images/ (PNGs)   │
  │  outputs/tables/ (CSVs)   │
  │  reports/ (text summary)  │
  └──────────────────────────┘
           │
           ▼
  ┌──────────────────────────┐
  │  STREAMLIT DASHBOARD      │   ← Interactive exploration
  │  app/streamlit_app.py     │
  └──────────────────────────┘
```

## Module Descriptions

### src/data_generator.py
- Generates 25 years of synthetic daily climate data
- Includes realistic seasonal cycles, warming trend, noise
- Injects anomalies: heatwave, cold snap, drought, flooding

### src/preprocessor.py
- Loads and validates raw CSV
- Removes duplicates, interpolates nulls
- Engineers: rolling averages, heat index, season, quarter
- Aggregates to monthly and yearly summaries

### src/trend_analysis.py
- Linear regression on yearly temperature and rainfall
- Returns slope (°C/year), R², p-value
- Seasonal trend: per-month warming over years
- Decade comparison table

### src/anomaly_detection.py
- Z-Score method (global statistical outliers)
- IQR method (robust box method)
- Rolling window method (temporal/local anomalies)
- Labels: Heatwave, Cold Snap, Heavy Rainfall, Drought

### src/forecasting.py
- Linear regression extrapolation (5-year horizon)
- Polynomial regression for non-linear projection
- Confidence interval estimation (±1.5σ)

### src/visualizer.py
- 10 production-quality PNG charts
- Saves to outputs/images/
- Functions callable individually or all at once

### app/streamlit_app.py
- Interactive 5-tab dashboard
- Real-time slider for date range and thresholds
- Displays all charts, tables, and KPI cards

### main.py
- Single orchestration script
- Runs all 8 pipeline phases in order
- Saves all outputs and generates text report
