import os, json, pickle
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "output", "results")

st.set_page_config(page_title="Economic Shock Analyzer", page_icon="📉", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

* { font-family: 'DM Sans', sans-serif; }
h1, h2, h3 { font-family: 'Syne', sans-serif !important; }
.stApp { background: #080808; color: #f0f0f0; }
[data-testid="stSidebar"] { background: #0f0f0f; border-right: 1px solid #1e1e1e; }

.hero {
    text-align: center;
    padding: 3rem 1rem 2rem;
    position: relative;
}
.hero::before {
    content: '';
    position: absolute;
    top: -60px; left: 50%; transform: translateX(-50%);
    width: 600px; height: 300px;
    background: radial-gradient(ellipse at center, rgba(120,40,255,0.35) 0%, rgba(80,0,200,0.15) 40%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
    z-index: 0;
}
.hero h1 {
    font-family: 'Syne', sans-serif;
    font-size: 3rem;
    font-weight: 800;
    background: linear-gradient(135deg, #ffffff 40%, #a855f7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    position: relative; z-index: 1;
}
.hero p { color: #888; font-size: 1rem; max-width: 500px; margin: 0.5rem auto 0; position: relative; z-index: 1; }

.input-card {
    background: #111;
    border: 1px solid #222;
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}
.input-card:hover { border-color: #7c3aed; transition: border-color 0.2s; }

.metric-card {
    background: linear-gradient(135deg, #111 60%, #1a0a2e);
    border: 1px solid #2a1a4a;
    border-radius: 16px;
    padding: 1.8rem;
    text-align: center;
    margin-bottom: 1rem;
}
.metric-card .label { color: #888; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.12em; }
.metric-card .value { font-family: 'Syne', sans-serif; font-size: 2.4rem; font-weight: 700; color: #a855f7; margin: 0.3rem 0; }
.metric-card .sub { color: #555; font-size: 0.78rem; }

.section-title { font-family: 'Syne', sans-serif; font-size: 1.4rem; font-weight: 700; color: #fff; margin: 2rem 0 1rem; }
.section-title span { color: #a855f7; }

.hint { color: #555; font-size: 0.78rem; margin-top: -0.5rem; margin-bottom: 1rem; }

hr { border-color: #1e1e1e !important; }

/* input fields */
.stNumberInput input {
    background: #1a1a1a !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 8px !important;
    color: #f0f0f0 !important;
}
.stNumberInput input:focus { border-color: #7c3aed !important; }

.stButton > button {
    background: linear-gradient(135deg, #7c3aed, #a855f7) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    padding: 0.7rem 2rem !important;
    width: 100%;
    font-size: 1rem !important;
}
.stButton > button:hover { opacity: 0.9; }
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_model():
    path = os.path.join(MODEL_DIR, "rf_model.pkl")
    if not os.path.exists(path):
        return None, None, None
    bundle = pickle.load(open(path, "rb"))
    return bundle["model"], bundle["features"], bundle["targets"]

@st.cache_data
def get_historical_means():
    df = pd.read_csv(os.path.join(DATA_DIR, "merged_data.csv"), index_col="year")
    return df.mean().to_dict()

model, features, targets = load_model()

if model is None:
    st.error("model not found — run ml_model.py first")
    st.stop()

means = get_historical_means()

# hero
st.markdown("""
<div class="hero">
    <h1>Economic Shock.<br>Impact Analyzer.</h1>
    <p>enter your own commodity prices and see how they affect inflation, GDP, unemployment and interest rates</p>
</div>
""", unsafe_allow_html=True)

st.divider()

# input section
st.markdown("<div class='section-title'>Enter <span>Commodity Prices</span></div>", unsafe_allow_html=True)
st.markdown("<div class='hint'>fill in the prices you want to simulate — leave blank to use historical averages</div>", unsafe_allow_html=True)

commodity_info = {
    "WTI":            ("🛢 WTI Oil",          "$/barrel",  means.get("WTI", 70.0)),
    "BRENT":          ("🛢 Brent Crude",       "$/barrel",  means.get("BRENT", 75.0)),
    "NATURAL_GAS":    ("🔥 Natural Gas",       "$/mmbtu",   means.get("NATURAL_GAS", 3.5)),
    "ALUMINUM":       ("🔩 Aluminum",          "$/tonne",   means.get("ALUMINUM", 2000.0)),
    "CORN":           ("🌽 Corn",              "$/bushel",  means.get("CORN", 280.0)),
    "COTTON":         ("🌿 Cotton",            "cents/lb",  means.get("COTTON", 80.0)),
    "SUGAR":          ("🍬 Sugar",             "cents/lb",  means.get("SUGAR", 18.0)),
    "COFFEE":         ("☕ Coffee",            "cents/lb",  means.get("COFFEE", 180.0)),
    "COPPER":         ("🪙 Copper",            "$/tonne",   means.get("COPPER", 7000.0)),
    "WHEAT":          ("🌾 Wheat",             "$/bushel",  means.get("WHEAT", 280.0)),
    "ALL_COMMODITIES":("📦 All Commodities",   "index",     means.get("ALL_COMMODITIES", 150.0)),
}

user_inputs = {}
cols_per_row = 3
feature_list = [f for f in features if f in commodity_info]
rows = [feature_list[i:i+cols_per_row] for i in range(0, len(feature_list), cols_per_row)]

for row in rows:
    cols = st.columns(cols_per_row)
    for i, feat in enumerate(row):
        label, unit, default = commodity_info[feat]
        with cols[i]:
            val = st.number_input(
                f"{label} ({unit})",
                min_value=0.0,
                value=float(round(default, 2)),
                step=0.1,
                format="%.2f",
                key=feat
            )
            user_inputs[feat] = val

st.markdown("<br>", unsafe_allow_html=True)

scenario = st.text_input("give this scenario a name", value="my_scenario", label_visibility="visible")
predict_btn = st.button("🔮 Predict Economic Impact")

st.divider()

# prediction
if predict_btn:
    input_df = pd.DataFrame([user_inputs])[features]
    prediction = model.predict(input_df)[0]
    result = dict(zip(targets, prediction))

    st.markdown("<div class='section-title'>Predicted <span>Economic Impact</span></div>", unsafe_allow_html=True)

    res_cols = st.columns(len(targets))
    icons = {"Inflation (CPI %)": "📈", "GDP Growth (% Annual)": "📊", "Unemployment Rate (%)": "👷", "Interest Rate (Real, %)": "🏦"}
    for i, (target, value) in enumerate(result.items()):
        with res_cols[i]:
            icon = icons.get(target, "📌")
            st.markdown(f"""
            <div class='metric-card'>
                <div class='label'>{icon} {target}</div>
                <div class='value'>{value:.2f}%</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # what changed vs historical average
    st.markdown("<div class='section-title'>vs <span>Historical Average</span></div>", unsafe_allow_html=True)

    # get historical prediction using means
    mean_inputs = pd.DataFrame([{f: means.get(f, user_inputs[f]) for f in features}])
    baseline = dict(zip(targets, model.predict(mean_inputs)[0]))

    fig = go.Figure()
    fig.add_trace(go.Bar(name="historical avg", x=targets, y=[baseline[t] for t in targets],
                         marker_color="#2a1a4a", marker_line_color="#7c3aed", marker_line_width=1))
    fig.add_trace(go.Bar(name="your scenario", x=targets, y=[result[t] for t in targets],
                         marker_color="#a855f7"))
    fig.update_layout(
        barmode="group",
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font_color="#888", legend_font_color="#aaa",
        xaxis=dict(gridcolor="#1e1e1e", color="#555"),
        yaxis=dict(gridcolor="#1e1e1e", color="#555", title="% value"),
        margin=dict(t=20, b=20),
        legend=dict(bgcolor="rgba(0,0,0,0)")
    )
    st.plotly_chart(fig, use_container_width=True)

    # save
    os.makedirs(RESULTS_DIR, exist_ok=True)
    out = {"inputs": user_inputs, "predictions": result, "baseline": baseline}
    json.dump(out, open(os.path.join(RESULTS_DIR, f"{scenario}_prediction.json"), "w"), indent=2)
    st.success(f"saved to output/results/{scenario}_prediction.json")

else:
    st.markdown("<div style='text-align:center;color:#444;padding:3rem;'>👆 enter your commodity prices above and hit predict</div>", unsafe_allow_html=True)

# saved scenarios
st.divider()
st.markdown("<div class='section-title'>Saved <span>Scenarios</span></div>", unsafe_allow_html=True)
files = [f for f in os.listdir(RESULTS_DIR) if f.endswith("_prediction.json")] if os.path.exists(RESULTS_DIR) else []
if files:
    rows_data = []
    for f in files:
        name = f.replace("_prediction.json", "")
        data = json.load(open(os.path.join(RESULTS_DIR, f)))
        row = {"scenario": name}
        row.update({f"input_{k}": v for k, v in data["inputs"].items()})
        row.update(data["predictions"])
        rows_data.append(row)
    st.dataframe(pd.DataFrame(rows_data), use_container_width=True)
else:
    st.markdown("<div style='color:#444;'>no saved scenarios yet</div>", unsafe_allow_html=True)