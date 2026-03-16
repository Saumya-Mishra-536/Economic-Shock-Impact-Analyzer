# 📉 Economic Shock Impact Analyzer
### ML-Powered Business Simulation with Monte Carlo Analysis

> *"If inflation rises by 5%, what happens to our revenue? What's the worst case? Best case?"*
> This tool answers exactly that — with real data, machine learning, and probabilistic simulation.

---

## 🧭 Table of Contents

- [Overview](#-overview)
- [Who Is It For](#-who-is-it-for)
- [Live Demo](#-live-demo)
- [Features](#-features)
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

The **Economic Shock Impact Analyzer** is an end-to-end AI simulation tool that models how macro-level economic shocks — inflation spikes, interest rate hikes, demand collapses — ripple through a business's financials.

Unlike simple what-if calculators, this tool combines:
- 📡 **Real macroeconomic data** from the World Bank API
- 🤖 **ML regression models** trained on historical macro–business relationships
- 🎲 **Monte Carlo simulation** (1,000+ scenarios) to quantify uncertainty
- 📊 **Interactive Streamlit dashboard** for scenario exploration

The output isn't a single answer — it's a **probability distribution** of outcomes, giving decision-makers a realistic range to plan around.

---

## 🎯 Who Is It For

| Persona | Use Case |
|---|---|
| 💼 Strategy & Finance Teams | Stress-test revenue forecasts under macro scenarios |
| 📦 Product Managers | Understand demand sensitivity to economic cycles |
| 🎓 MBA / Economics Students | Applied macro-business analysis for portfolios |
| 📈 Financial Analysts | Complement DCF models with probabilistic scenario analysis |

---

## 🚀 Live Demo

> 🌐 **[Launch Dashboard →](https://your-app.streamlit.app)** *(deploy link after Streamlit Cloud setup)*

---

## ✨ Features

- **Real-world data ingestion** — pulls live indicators from the World Bank API (inflation, GDP growth, interest rates, unemployment)
- **Trained ML model** — Random Forest / Gradient Boosting regression predicts revenue impact % from macro inputs
- **Monte Carlo engine** — runs 1,000+ randomized scenarios and outputs a full probability distribution
- **Risk scoring** — assigns a quantified risk score based on volatility of outcomes
- **Interactive dashboard** — sliders, KPI cards, histograms, heatmaps, and scenario comparison tables
- **Scenario comparison** — run multiple named scenarios side by side

---

## 🏗 Project Architecture

```
economic-shock-analyzer/
│
├── data/
│   └── macro_data.csv           # Real data fetched from World Bank API
│
├── models/
│   └── rf_model.pkl             # Serialized trained ML model
│
├── output/
│   ├── charts/                  # Saved plots and visualizations
│   └── results/                 # Monte Carlo simulation results (JSON/CSV)
│
├── analysis/
│   ├── fetch_data.py            # Phase 1 — Pull & clean World Bank data
│   ├── ml_model.py              # Phase 2 — Train & evaluate ML model
│   └── monte_carlo.py           # Phase 3 — Run probabilistic simulations
│
├── app.py                       # Phase 4 — Streamlit dashboard
├── requirements.txt
└── README.md
```

**Data flow:**

```
World Bank API → fetch_data.py → macro_data.csv
                                       ↓
                               ml_model.py → rf_model.pkl
                                       ↓
                             monte_carlo.py → results/
                                       ↓
                                    app.py (dashboard)
```

---

## 🧰 Tech Stack

| Layer | Tool | Purpose |
|---|---|---|
| Language | Python 3.10+ | Core language |
| Data Fetching | `wbgapi` | World Bank macroeconomic data |
| Data Processing | `pandas`, `numpy` | Cleaning, transformations |
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

---

## 📖 Usage Guide

Run each phase in order:

### Phase 1 — Fetch Real Data
```bash
python3 analysis/fetch_data.py
```
Downloads macroeconomic indicators from the World Bank API and saves to `data/macro_data.csv`.

### Phase 2 — Train the ML Model
```bash
python3 analysis/ml_model.py
```
Trains a regression model on historical macro data, evaluates it (MAE, RMSE, R²), and saves the model to `models/rf_model.pkl`.

### Phase 3 — Run Monte Carlo Simulation
```bash
python3 analysis/monte_carlo.py
```
Runs 1,000+ randomized scenarios and writes results to `output/results/`.

### Phase 4 — Launch the Dashboard
```bash
streamlit run app.py
```
Opens the interactive dashboard at `http://localhost:8501`.

---

## 🔬 How It Works

### Phase 1 — Real Macroeconomic Data

Data is pulled from the **World Bank Open Data API** using `wbgapi`:

| Indicator | World Bank Code |
|---|---|
| Inflation rate (%) | `FP.CPI.TOTL.ZG` |
| GDP growth (%) | `NY.GDP.MKTP.KD.ZG` |
| Real interest rate (%) | `FR.INR.RINR` |
| Unemployment rate (%) | `SL.UEM.TOTL.ZS` |

### Phase 2 — ML Model

- **Target:** Predicted Revenue Impact (%)
- **Features:** Inflation %, Interest Rate %, GDP Growth %, Unemployment %
- **Pipeline:** `StandardScaler` → `RandomForestRegressor` or `GradientBoostingRegressor`
- **Evaluation metrics:** MAE, RMSE, R²

The model learns from historical country-level data how macro conditions have historically correlated with business revenue changes.

### Phase 3 — Monte Carlo Simulation

- Samples 1,000+ random combinations of macro inputs (drawn from calibrated distributions)
- Applies the trained ML model to each scenario
- Aggregates results into:
  - 📈 Best case (95th percentile)
  - 📉 Worst case (5th percentile)
  - 🎯 Most likely outcome (median)
  - ⚠️ Risk Score (based on output variance)

### Phase 4 — Dashboard

| Component | Description |
|---|---|
| Sidebar sliders | Adjust Inflation %, Interest Rate %, Demand Shock % |
| KPI cards | Revenue impact, Cost impact, Profit impact |
| Histogram | Monte Carlo distribution of revenue outcomes |
| Line chart | Scenario comparisons over time |
| Heatmap | Risk exposure across macro combinations |
| Comparison table | Side-by-side named scenario results |

---

## 🗺 Roadmap

- [x] World Bank API integration
- [x] Random Forest / Gradient Boosting ML model
- [x] Monte Carlo simulation engine
- [x] Streamlit dashboard with scenario sliders
- [ ] Sector-specific impact models (retail, SaaS, manufacturing)
- [ ] Export simulation results to PDF / Excel
- [ ] Multi-country comparison mode
- [ ] GPT-powered natural language scenario interpreter
- [ ] Historical back-testing against actual business data

---

## 👩‍💻 Author

**Saumya Mishra**
Internship Portfolio Project — Economic Shock Impact Analyzer

---

*Built with real data. Powered by ML. Designed for decisions.*
