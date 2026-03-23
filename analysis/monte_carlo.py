import os, json, pickle
import numpy as np
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "output", "results")

def load_model():
    path = os.path.join(MODEL_DIR, "rf_model.pkl")
    if not os.path.exists(path):
        raise FileNotFoundError("rf_model.pkl not found — run ml_model.py first")
    bundle = pickle.load(open(path, "rb"))
    return bundle["model"], bundle["features"], bundle["targets"]

def get_base_stats(features):
    df = pd.read_csv(os.path.join(DATA_DIR, "merged_data.csv"), index_col="year")
    return df[features].mean(), df[features].std()

def run_simulation(model, features, targets, shocks=None, n=1000):
    means, stds = get_base_stats(features)
    np.random.seed(42)

    rows = []
    for _ in range(n):
        sample = {}
        for col in features:
            if shocks and col in shocks:
                shock_pct, shock_std = shocks[col]
                sample[col] = means[col] * (1 + np.random.normal(shock_pct, shock_std) / 100)
            else:
                sample[col] = np.random.normal(means[col], stds[col])
        rows.append(sample)

    X = pd.DataFrame(rows, columns=features)
    preds = model.predict(X)
    results = pd.DataFrame(preds, columns=targets)
    return pd.concat([X, results], axis=1)

def summarize(results, targets):
    summary = {}
    for col in targets:
        v = results[col]
        summary[col] = {
            "mean": round(v.mean(), 3),
            "median": round(v.median(), 3),
            "best_case": round(v.quantile(0.95), 3),
            "worst_case": round(v.quantile(0.05), 3),
            "risk_score": round(v.std() / abs(v.mean() + 1e-9), 3)
        }
    return summary

def main(shocks=None, scenario="default"):
    model, features, targets = load_model()
    print(f"running {1000} simulations for scenario: {scenario}")

    results = run_simulation(model, features, targets, shocks)
    summary = summarize(results, targets)

    os.makedirs(RESULTS_DIR, exist_ok=True)
    results.to_csv(os.path.join(RESULTS_DIR, f"{scenario}_simulations.csv"), index=False)
    json.dump(summary, open(os.path.join(RESULTS_DIR, f"{scenario}_summary.json"), "w"), indent=2)

    print("\nresults:")
    for target, stats in summary.items():
        print(f"\n  {target}")
        for k, v in stats.items():
            print(f"    {k}: {v}")
    print(f"\nsaved to output/results/")

if __name__ == "__main__":
    # try changing the shock values to simulate different scenarios
    shocks = {"WTI": (40, 10), "BRENT": (40, 10)}
    main(shocks=shocks, scenario="oil_spike_40pct")