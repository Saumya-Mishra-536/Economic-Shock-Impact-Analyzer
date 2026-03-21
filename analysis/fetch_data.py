import pandas as pd
import numpy as np
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

def load_data(filepath):
    df = pd.read_csv(filepath, parse_dates=["date"])
    df = df.sort_values("date").set_index("date")
    df = df.select_dtypes(include="number")
    df.dropna(how="all", inplace=True)

    # monthly → yearly average
    df = df.resample("YE").mean()
    df.index = df.index.year
    df.index.name = "year"
    df = df.ffill().bfill()

    print(f"Loaded {len(df)} years of data with columns: {list(df.columns)}")
    return df


def add_macro_columns(df):
    # we derive 4 economic indicators from commodity prices
    # the logic is simple — expensive oil/gas = more inflation, less growth

    # oil signal
    oil = df[["WTI", "BRENT"]].mean(axis=1) if "WTI" in df.columns else pd.Series(70, index=df.index)
    oil_dev = ((oil - oil.mean()) / oil.mean()) * 100

    # gas signal
    gas = df["NATURAL_GAS"] if "NATURAL_GAS" in df.columns else pd.Series(3.0, index=df.index)
    gas_dev = ((gas - gas.mean()) / gas.mean()) * 100

    # food signal
    food_cols = [c for c in ["CORN", "WHEAT", "SUGAR", "COFFEE"] if c in df.columns]
    food = df[food_cols].mean(axis=1) if food_cols else pd.Series(100, index=df.index)
    food_dev = ((food - food.mean()) / food.mean()) * 100

    # metals signal
    metals_cols = [c for c in ["ALUMINUM", "COPPER"] if c in df.columns]
    metals = df[metals_cols].mean(axis=1) if metals_cols else pd.Series(2000, index=df.index)
    metals_dev = ((metals - metals.mean()) / metals.mean()) * 100

    np.random.seed(42)
    n = len(df)

    # inflation goes up when oil, gas, food are expensive
    df["Inflation (CPI %)"] = (4.0 + 0.04*oil_dev + 0.03*gas_dev + 0.02*food_dev + np.random.normal(0, 0.3, n)).clip(0, 25)

    # gdp growth drops when energy is expensive, rises when metals demand is high
    df["GDP Growth (% Annual)"] = (3.5 - 0.03*oil_dev + 0.01*metals_dev - 0.02*gas_dev + np.random.normal(0, 0.3, n)).clip(-10, 12)

    # unemployment rises when growth falls (okun's law)
    df["Unemployment Rate (%)"] = (7.0 - 0.5*(df["GDP Growth (% Annual)"] - 3.5) + np.random.normal(0, 0.3, n)).clip(2, 20)

    # interest rate follows inflation and growth (taylor rule)
    df["Interest Rate (Real, %)"] = (2.0 + 0.5*(df["Inflation (CPI %)"] - 4.0) - 0.5*(df["GDP Growth (% Annual)"] - 3.5) + np.random.normal(0, 0.2, n)).clip(-5, 20)

    print(f"Derived macro columns: Inflation, GDP Growth, Unemployment, Interest Rate")
    return df


def main():
    path = os.path.join(DATA_DIR, "commodity_prices.csv")
    out  = os.path.join(DATA_DIR, "merged_data.csv")

    if not os.path.exists(path):
        raise FileNotFoundError("Please put commodity_prices.csv inside the data/ folder")

    df = load_data(path)
    df = add_macro_columns(df)

    df.to_csv(out)
    print(f"\nSaved to {out}")
    print(df.head())


if __name__ == "__main__":
    main()
