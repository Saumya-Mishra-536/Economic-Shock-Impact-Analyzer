# 📉 Economic Shock Impact Analyzer
### ML-Powered Business Simulation with Monte Carlo Analysis

---

## 📌 Project Overview

The **Economic Shock Impact Analyzer** is an AI-powered simulation tool that predicts how macro-level economic events — like inflation spikes, interest rate changes, or demand shocks — affect a business's revenue, costs, and profit.

It connects **real-world macroeconomic data** with **machine learning** and **Monte Carlo simulation** to give businesses a range of possible outcomes under economic stress — not just one fixed answer.

> **"If inflation rises by 5%, what happens to our revenue? What's the worst case? Best case?"**
> This tool answers exactly that.

---

## 🎯 Who Is It For?

- Strategy & Business Planning Teams
- Product Managers (finance, e-commerce, SaaS)
- Finance Analysts
- MBA / Economics students doing applied business analysis

---

## 🏗️ Project Phases

### Phase 1 — Real Dataset (World Bank API)
- Fetch live macroeconomic data using the **World Bank API**
- Indicators: Inflation rate, GDP growth, Interest rate, Unemployment rate
- Clean and prepare data for modeling

### Phase 2 — ML Model (Regression)
- Train a **Random Forest / Gradient Boosting** regression model
- Predict revenue impact % based on macro indicators
- Evaluate using MAE, RMSE, R²

### Phase 3 — Monte Carlo Simulation
- Run **1000+ random scenarios** with varying inflation, interest rates
- Output: probability distribution of revenue impact
- Results: Best case / Worst case / Most likely outcome + Risk Score

### Phase 4 — Interactive Dashboard
- Build a **Streamlit** dashboard with sliders, KPI cards, and charts
- Scenario comparison and side-by-side visualization
- Deploy on **Streamlit Community Cloud**

---

## 📁 Project Structure

```
economic-shock-analyzer/
│
├── data/
│   └── macro_data.csv              # Real data from World Bank API
│
├── models/
│   └── rf_model.pkl                # Saved trained ML model
│
├── output/
│   ├── charts/                     # Generated charts and plots
│   └── results/                    # Simulation results
│
├── analysis/
│   ├── fetch_data.py               # Phase 1: Pull World Bank data
│   ├── ml_model.py                 # Phase 2: Train ML model
│   └── monte_carlo.py              # Phase 3: Run simulations
│
├── app.py                          # Phase 4: Streamlit dashboard
├── requirements.txt                # All dependencies
└── README.md
```

---

## 🧰 Tech Stack

| Category | Tool | Purpose |
|---|---|---|
| Language | Python 3 | Core language |
| Real Data | `wbgapi` | Fetch World Bank macroeconomic data |
| Data Processing | `pandas`, `numpy` | Clean and manipulate data |
| ML Models | `scikit-learn` | Random Forest / Gradient Boosting regression |
| Statistics | `scipy` | Monte Carlo simulation & distributions |
| Dashboard UI | `streamlit` | Interactive web dashboard |
| Charts | `plotly`, `matplotlib` | Line charts, heatmaps, histograms |

---

## 📦 Requirements

Create a file called `requirements.txt` in your root folder with:

```
pandas
numpy
scipy
scikit-learn
streamlit
plotly
matplotlib
wbgapi
```

Install everything with one command:
```bash
pip3 install -r requirements.txt
```

---

## 🌍 Real Data Used (World Bank API)

| Indicator | World Bank Code |
|---|---|
| Inflation rate (%) | `FP.CPI.TOTL.ZG` |
| GDP growth (%) | `NY.GDP.MKTP.KD.ZG` |
| Real interest rate (%) | `FR.INR.RINR` |
| Unemployment rate (%) | `SL.UEM.TOTL.ZS` |

---

## 🤖 ML Model Details

- **Target:** Predicted Revenue Impact (%)
- **Features:** Inflation %, Interest Rate %, GDP Growth %, Unemployment %
- **Models:** Random Forest Regressor, Gradient Boosting Regressor
- **Evaluation:** MAE, RMSE, R²
- **Pipeline:** StandardScaler → Model (using sklearn Pipeline)

---

## 🎲 Monte Carlo Simulation

- Runs **1000 scenarios** with randomly varied macro inputs
- Each run applies economic formulas to calculate revenue/cost/profit impact
- Outputs:
  - Probability distribution of revenue impact
  - Best case / Worst case / Most likely outcome
  - Risk score for the business

---

## 📊 Dashboard Features

- **Sidebar sliders:** Inflation %, Interest Rate %, Demand Shock %
- **KPI cards:** Revenue, Costs, Profit impact
- **Line chart:** Scenario comparisons over time
- **Histogram:** Monte Carlo outcome distribution
- **Heatmap:** Risk exposure across scenarios
- **Table:** Side-by-side scenario comparison

---

## ▶️ How to Run

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/economic-shock-analyzer.git
cd economic-shock-analyzer
```

### 2. Install Dependencies
```bash
pip3 install -r requirements.txt
```

### 3. Fetch Real Data
```bash
python3 analysis/fetch_data.py
```

### 4. Train the ML Model
```bash
python3 analysis/ml_model.py
```

### 5. Run Monte Carlo Simulation
```bash
python3 analysis/monte_carlo.py
```

### 6. Launch the Dashboard
```bash
streamlit run app.py
```

---

## 🌐 Deployment

Deployed on **Streamlit Community Cloud** (free):
1. Push code to GitHub
2. Go to [streamlit.io/cloud](https://streamlit.io/cloud)
3. Connect your GitHub repo
4. Click Deploy ✅

---

## 📈 Why This Project Stands Out

| Feature | Basic Version | This Version |
|---|---|---|
| Data source | Made-up numbers | Real World Bank API |
| Analysis | Fixed formulas | ML regression model |
| Uncertainty | Single answer | 1000 Monte Carlo scenarios |
| Output | Static table | Interactive Streamlit dashboard |
| Deployment | Localhost only | Live on Streamlit Cloud |
| **Rating** | 7.5 / 10 | **9 / 10** |

---

## 👩‍💻 Author

**Saumya Mishra**
Economic Shock Impact Analyzer — Internship Portfolio Project