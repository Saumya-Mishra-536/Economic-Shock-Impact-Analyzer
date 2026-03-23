import os, pickle
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")

features = ["WTI", "BRENT", "NATURAL_GAS", "ALUMINUM", "CORN", "COTTON", "SUGAR", "COPPER", "WHEAT", "ALL_COMMODITIES"]
targets = ["Inflation (CPI %)", "GDP Growth (% Annual)", "Unemployment Rate (%)", "Interest Rate (Real, %)"]

def load_data():
    df = pd.read_csv(os.path.join(DATA_DIR, "merged_data.csv"), index_col="year")
    f = [c for c in features if c in df.columns]
    t = [c for c in targets if c in df.columns]
    df = df[f + t].dropna()
    print(f"got {len(df)} years of data, {len(f)} features, {len(t)} targets")
    return df[f], df[t], f, t

def train(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = Pipeline([("scaler", StandardScaler()), ("rf", RandomForestRegressor(n_estimators=200, max_depth=6, random_state=42))])
    model.fit(X_train, y_train)
    return model, X_test, y_test

def evaluate(model, X_test, y_test, t):
    preds = model.predict(X_test)
    print("\nresults:")
    for i, col in enumerate(t):
        mae = mean_absolute_error(y_test.iloc[:, i], preds[:, i])
        rmse = np.sqrt(mean_squared_error(y_test.iloc[:, i], preds[:, i]))
        r2 = r2_score(y_test.iloc[:, i], preds[:, i])
        print(f"  {col} → MAE: {mae:.3f}  RMSE: {rmse:.3f}  R²: {r2:.3f}")

def save_model(model, f, t):
    os.makedirs(MODEL_DIR, exist_ok=True)
    path = os.path.join(MODEL_DIR, "rf_model.pkl")
    pickle.dump({"model": model, "features": f, "targets": t}, open(path, "wb"))
    print(f"\nsaved to {path}")

def main():
    X, y, f, t = load_data()
    model, X_test, y_test = train(X, y)
    evaluate(model, X_test, y_test, t)
    save_model(model, f, t)

if __name__ == "__main__":
    main()