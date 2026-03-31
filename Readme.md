# 📉 Economic Shock Impact Analyzer
### ML-Powered Business Simulation with Monte Carlo Analysis

> *"If oil prices spike 40%, what happens to India's GDP growth? What's the worst case? Best case?"*
> This tool answers exactly that — with real commodity & macro data, machine learning, and probabilistic simulation.

---

## 🧭 Table of Contents

- [Overview](#-overview)
- [Who Is It For](#-who-is-it-for)
- [Live Demo](#-live-demo)
- [Features](#-features)
- [Datasets](#-datasets)
- [Project Architecture](#-project-architecture)
- [Tech Stack](#-tech-stack)
- [Setup & Installation](#-setup--installation)
- [Usage Guide](#-usage-guide)
- [How It Works](#-how-it-works)
- [Dashboard Preview](#-dashboard-preview)
- [Roadmap](#-roadmap)
- [Author](#-author)

---

## 🔍 Overview

The **Economic Shock Impact Analyzer** is an end-to-end AI simulation tool that models how global commodity shocks — oil price spikes, food price collapses, metal price surges — ripple through macroeconomic indicators like GDP growth, inflation, and unemployment, with a focus on **India and emerging economies**.

Unlike simple what-if calculators, this tool combines:
- 📡 **Real commodity & macroeconomic data** from AlphaVantage and World Bank (via Kaggle)
- 🤖 **ML regression models** trained on historical commodity–macro relationships (1980–2023)
- 🎲 **Monte Carlo simulation** (1,000+ scenarios) to quantify uncertainty
- 📊 **Interactive Streamlit dashboard** for scenario exploration

The output isn't a single answer — it's a **probability distribution** of outcomes, giving decision-makers a realistic range to plan around.

---

## 🎯 Who Is It For

| Persona | Use Case |
|---|---|
| 💼 Strategy & Finance Teams | Stress-test revenue forecasts under macro scenarios |
| 📦 Policy Analysts | Understand sectoral sensitivity to global commodity cycles |
| 🎓 MBA / Economics Students | Applied macro-business analysis for portfolios |
| 📈 Financial Analysts | Complement DCF models with probabilistic scenario analysis |



## 🌍 Why This Matters

Global economies are highly sensitive to commodity shocks:

- 🛢️ Oil spikes → Inflation surges, growth slows  
- 🌾 Food shocks → Social + policy instability  
- 🏗 Metals surge → Manufacturing cost pressure  

Traditional models give **single forecasts** — but real-world outcomes are uncertain.

This tool embraces uncertainty by providing:
- 📉 Downside risk (worst-case scenarios)
- 📈 Upside potential (best-case outcomes)
- 🎯 Most probable macro trajectory

👉 Making it useful for **strategy, policy, and investment decisions**

---

## 🚀 Live Demo

> 🌐 **[Launch Dashboard →](https://your-app.streamlit.app)** *(deploy link after Streamlit Cloud setup)*

---

## ✨ Features

- **Dual dataset pipeline** — combines commodity price shocks (AlphaVantage) with macro impact indicators (World Bank) for a full cause-effect model
- **Trained ML model** — Random Forest / Gradient Boosting regression predicts macro impact (GDP growth, inflation) from commodity shock inputs
- **Monte Carlo engine** — runs 1,000+ randomized scenarios and outputs a full probability distribution
- **Risk scoring** — assigns a quantified risk score based on volatility of outcomes
- **Interactive dashboard** — sliders, KPI cards, histograms, heatmaps, and scenario comparison tables
- **Scenario comparison** — run multiple named scenarios side by side (e.g., "2008 Oil Crash" vs "2022 Ukraine Shock")

---

## 📦 Datasets

This project uses **two Kaggle datasets** that together form a complete shock → impact pipeline:

### 1. 🛢️ Commodity Prices Dataset *(Shock Input)*
**Source:** AlphaVantage via Kaggle
**Coverage:** January 1980 – April 2023 (monthly)

| Column | Description |
|---|---|
| `WTI` | West Texas Intermediate crude oil price ($/bbl) |
| `BRENT` | Brent crude oil price ($/bbl) |
| `NATURAL_GAS` | Natural gas price ($/mmbtu) |
| `ALUMINUM` | Aluminum price — industrial/metals shock |
| `CORN` | Corn price — food/agriculture shock |
| `COTTON` | Cotton price — India's key export commodity |
| `SUGAR` | Sugar price — India is world's largest producer |
| `COFFEE` | Coffee price |
| `ALL_COMMODITIES` | Composite commodity price index |

> This dataset captures every major global shock: 1990 Gulf War oil spike, 2008 commodity supercycle crash, 2020 COVID collapse, 2022 Russia-Ukraine commodity surge.

---

### 2. 🌍 Global Economic Indicators Dataset *(Shock Impact / Output)*
**Source:** World Bank via Kaggle
**Coverage:** 2010–2025 (annual, 100+ countries)

| Column | Description |
|---|---|
| `country_name` | Full country name (e.g., India, United States) |
| `country_id` | ISO 2-letter country code (e.g., IN, US) |
| `year` | Year (2010–2025) |
| `Inflation (CPI %)` | Annual consumer price inflation |
| `GDP (Current USD)` | Gross Domestic Product in current USD |
| `GDP per Capita (Current USD)` | GDP divided by total population |
| `Unemployment Rate (%)` | Percentage of labor force unemployed |
| `Interest Rate (Real, %)` | Lending interest rate adjusted for inflation |
| `Inflation (GDP Deflator, %)` | Inflation based on GDP deflator |
| `GDP Growth (% Annual)` | Year-over-year GDP growth rate |

---

### 🔗 How the Datasets Connect

```
Commodity Price Shock        →    Macroeconomic Impact
(AlphaVantage, 1980–2023)        (World Bank, 2010–2025)

WTI / BRENT spike           →    GDP Growth ↓, Inflation ↑
ALUMINUM surge              →    Manufacturing sector stress
COTTON / SUGAR shock        →    India agriculture stress
ALL_COMMODITIES index       →    Unemployment Rate ↑

Merged working range: 2010–2023 (13 years, resampled to annual)
```

---

## 🏗 Project Architecture

```
economic-shock-analyzer/
│
├── data/
│   ├── commodity_prices.csv      # AlphaVantage commodity data (1980–2023, monthly)
│   └── macro_indicators.csv      # World Bank macro data (2010–2025, annual)
│
├── models/
│   └── rf_model.pkl              # Serialized trained ML model
│
├── output/
│   ├── charts/                   # Saved plots and visualizations
│   └── results/                  # Monte Carlo simulation results (JSON/CSV)
│
├── analysis/
│   ├── fetch_data.py             # Phase 1 — Load, clean & merge both datasets
│   ├── ml_model.py               # Phase 2 — Train & evaluate ML model
│   └── monte_carlo.py            # Phase 3 — Run probabilistic simulations
│
├── app.py                        # Phase 4 — Streamlit dashboard
├── requirements.txt
└── README.md
```

**Data flow:**

```
commodity_prices.csv ──┐
                        ├──► fetch_data.py ──► merged_data.csv
macro_indicators.csv ──┘           │
                                   ▼
                           ml_model.py ──► rf_model.pkl
                                   │
                                   ▼
                         monte_carlo.py ──► results/
                                   │
                                   ▼
                              app.py (dashboard)
```

---

## 🧰 Tech Stack

| Layer | Tool | Purpose |
|---|---|---|
| Language | Python 3.10+ | Core language |
| Data Processing | `pandas`, `numpy` | Cleaning, resampling, merging datasets |
| ML Models | `scikit-learn` | Random Forest / Gradient Boosting regression |
| Statistics | `scipy` | Distributions and Monte Carlo sampling |
| Dashboard | `streamlit` | Interactive web UI |
| Charts | `plotly`, `matplotlib` | Line charts, histograms, heatmaps |

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.10 or higher
- `pip` package manager

### 1. Clone the Repository

```bash
git clone https://github.com/Saumya-Mishra-536/Economic-Shock-Impact-Analyzer.git
cd Economic-Shock-Impact-Analyzer
```

### 2. (Recommended) Create a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Add the Datasets

Download both datasets from Kaggle and place them in the `data/` folder:
- `data/commodity_prices.csv` — AlphaVantage commodity prices dataset
- `data/macro_indicators.csv` — World Bank global economic indicators dataset

---

## 📖 Usage Guide

Run each phase in order:

### Phase 1 — Load & Merge Data
```bash
python3 analysis/fetch_data.py
```
Loads both CSVs, resamples commodity data from monthly to annual, merges on year, and saves to `data/merged_data.csv`.

### Phase 2 — Train the ML Model
```bash
python3 analysis/ml_model.py
```
Trains a regression model on the merged dataset, evaluates it (MAE, RMSE, R²), and saves the model to `models/rf_model.pkl`.

### Phase 3 — Run Monte Carlo Simulation
```bash
python3 analysis/monte_carlo.py
```
Runs 1,000+ randomized commodity shock scenarios and writes results to `output/results/`.

### Phase 4 — Launch the Dashboard
```bash
streamlit run app.py
```
Opens the interactive dashboard at `http://localhost:8501`.

---

## 🔬 How It Works

### Phase 1 — Data Preparation

**Commodity dataset** (monthly → annual resampling):

| Shock Variable | Commodity Column |
|---|---|
| Energy shock | `WTI`, `BRENT`, `NATURAL_GAS` |
| Metals shock | `ALUMINUM` |
| Food/Agri shock | `CORN`, `COTTON`, `SUGAR` |
| Composite shock | `ALL_COMMODITIES` |

**Macro dataset** (annual, used as target variables):

| Impact Variable | Column |
|---|---|
| GDP Growth | `GDP Growth (% Annual)` |
| Inflation | `Inflation (CPI %)` |
| Unemployment | `Unemployment Rate (%)` |
| Interest Rate | `Interest Rate (Real, %)` |

Both datasets are merged on `year`, with commodity prices serving as **features (X)** and macro indicators as **targets (y)**.

### Phase 2 — ML Model

- **Features (X):** Annual commodity prices — WTI, Brent, Natural Gas, Aluminum, Corn, Cotton, Sugar
- **Target (y):** GDP Growth %, Inflation %, Unemployment Rate %
- **Pipeline:** `StandardScaler` → `RandomForestRegressor` or `GradientBoostingRegressor`
- **Evaluation metrics:** MAE, RMSE, R²

The model learns how commodity price changes have historically transmitted into macroeconomic outcomes across countries.

### Phase 3 — Monte Carlo Simulation

- Samples 1,000+ random combinations of commodity price shocks (drawn from calibrated distributions)
- Applies the trained ML model to each scenario
- Aggregates results into:
  - 📈 Best case (95th percentile)
  - 📉 Worst case (5th percentile)
  - 🎯 Most likely outcome (median)
  - ⚠️ Risk Score (based on output variance)

### Phase 4 — Dashboard

| Component | Description |
|---|---|
| Sidebar sliders | Adjust WTI oil price, commodity index, food prices |
| KPI cards | GDP impact, inflation delta, unemployment shift |
| Histogram | Monte Carlo distribution of macro outcomes |
| Line chart | Commodity price trends vs macro indicators over time |
| Heatmap | Risk exposure across commodity combinations |
| Comparison table | Side-by-side named scenario results |

---

## 🗺 Roadmap

- [x] Commodity price data pipeline (AlphaVantage, 1980–2023)
- [x] World Bank macro indicators integration (2010–2025)
- [x] Annual merge & preprocessing pipeline
- [x] Random Forest / Gradient Boosting ML model
- [x] Monte Carlo simulation engine
- [x] Streamlit dashboard with scenario sliders
- [ ] India-specific sectoral stress models (agriculture, manufacturing, services)
- [ ] Export simulation results to PDF / Excel
- [ ] Multi-country comparison mode
- [ ] GPT-powered natural language scenario interpreter
- [ ] Historical back-testing against documented shock events (2008, 2020, 2022)



---

*Built with real commodity & macro data. Powered by ML. Designed for decisions.*
