import os, json, pickle
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
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
    text-align: center; padding: 3rem 1rem 2rem; position: relative;
}
.hero::before {
    content: ''; position: absolute;
    top: -60px; left: 50%; transform: translateX(-50%);
    width: 600px; height: 300px;
    background: radial-gradient(ellipse at center, rgba(120,40,255,0.35) 0%, rgba(80,0,200,0.15) 40%, transparent 70%);
    border-radius: 50%; pointer-events: none; z-index: 0;
}
.hero h1 {
    font-family: 'Syne', sans-serif; font-size: 3rem; font-weight: 800;
    background: linear-gradient(135deg, #ffffff 40%, #a855f7);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    position: relative; z-index: 1;
}
.hero p { color: #888; font-size: 1rem; max-width: 500px; margin: 0.5rem auto 0; position: relative; z-index: 1; }

.metric-card {
    background: linear-gradient(135deg, #111 60%, #1a0a2e);
    border: 1px solid #2a1a4a; border-radius: 16px;
    padding: 1.5rem; text-align: center; margin-bottom: 1rem;
}
.metric-card .label { color: #888; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.12em; }
.metric-card .value { font-family: 'Syne', sans-serif; font-size: 2.2rem; font-weight: 700; color: #a855f7; margin: 0.3rem 0; }
.metric-card .sub { color: #555; font-size: 0.78rem; }

.section-title { font-family: 'Syne', sans-serif; font-size: 1.4rem; font-weight: 700; color: #fff; margin: 2rem 0 0.5rem; }
.section-title span { color: #a855f7; }

.tab-hint { color: #555; font-size: 0.82rem; margin-bottom: 1.2rem; }

hr { border-color: #1e1e1e !important; }

.stNumberInput input {
    background: #1a1a1a !important; border: 1px solid #2a2a2a !important;
    border-radius: 8px !important; color: #f0f0f0 !important;
}
.stNumberInput input:focus { border-color: #7c3aed !important; }

/* tab styling */
.stTabs [data-baseweb="tab-list"] { background: #111; border-radius: 12px; padding: 4px; gap: 4px; border: 1px solid #222; }
.stTabs [data-baseweb="tab"] { background: transparent; color: #666; border-radius: 8px; font-family: 'Syne', sans-serif; font-weight: 600; }
.stTabs [aria-selected="true"] { background: linear-gradient(135deg, #7c3aed, #a855f7) !important; color: white !important; }

.stButton > button {
    background: linear-gradient(135deg, #7c3aed, #a855f7) !important;
    color: white !important; border: none !important; border-radius: 8px !important;
    font-family: 'Syne', sans-serif !important; font-weight: 600 !important;
    padding: 0.7rem 2rem !important; width: 100%; font-size: 1rem !important;
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
def load_history():
    return pd.read_csv(os.path.join(DATA_DIR, "merged_data.csv"), index_col="year")

model, features, targets = load_model()

if model is None:
    st.error("model not found — run ml_model.py first")
    st.stop()

df = load_history()
means = df.mean().to_dict()

plot_theme = dict(
    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    font_color="#888", xaxis=dict(gridcolor="#1e1e1e", color="#555"),
    yaxis=dict(gridcolor="#1e1e1e", color="#555"),
    margin=dict(t=40, b=20), legend=dict(bgcolor="rgba(0,0,0,0)", font_color="#aaa")
)

# ── hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>Economic Shock.<br>Impact Analyzer.</h1>
    <p>explore historical trends, simulate future commodity prices, and predict macro economic outcomes</p>
</div>
""", unsafe_allow_html=True)

st.divider()

# ── section 1: historical overview ───────────────────────────────────────────
st.markdown("<div class='section-title'>Historical <span>Overview</span></div>", unsafe_allow_html=True)
st.markdown("<div class='tab-hint'>a snapshot of how macro indicators have moved over the years</div>", unsafe_allow_html=True)

# summary metric cards — latest year values
latest = df.iloc[-1]
icons = {"Inflation (CPI %)": "📈", "GDP Growth (% Annual)": "📊", "Unemployment Rate (%)": "👷", "Interest Rate (Real, %)": "🏦"}
card_cols = st.columns(len(targets))
for i, t in enumerate(targets):
    with card_cols[i]:
        val = latest.get(t, 0)
        avg = df[t].mean()
        diff = val - avg
        arrow = "↑" if diff > 0 else "↓"
        color = "#ef4444" if diff > 0 and t != "GDP Growth (% Annual)" else "#22c55e"
        st.markdown(f"""
        <div class='metric-card'>
            <div class='label'>{icons.get(t,"")} {t}</div>
            <div class='value'>{val:.2f}%</div>
            <div class='sub' style='color:{color}'>{arrow} {abs(diff):.2f}% vs avg</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── section 2: explore by indicator ──────────────────────────────────────────
st.markdown("<div class='section-title'>Explore <span>by Indicator</span></div>", unsafe_allow_html=True)
st.markdown("<div class='tab-hint'>pick an indicator to see its full historical trend</div>", unsafe_allow_html=True)

tab_labels = [f"{icons.get(t,'')} {t.split('(')[0].strip()}" for t in targets]
tabs = st.tabs(tab_labels)

for i, (tab, target) in enumerate(zip(tabs, targets)):
    with tab:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df.index, y=df[target],
            mode="lines+markers",
            line=dict(color="#a855f7", width=2.5),
            marker=dict(size=5, color="#7c3aed"),
            fill="tozeroy",
            fillcolor="rgba(120,40,255,0.08)",
            name=target
        ))
        # add average line
        avg_val = df[target].mean()
        fig.add_hline(y=avg_val, line_dash="dash", line_color="#444",
                      annotation_text=f"avg {avg_val:.2f}%", annotation_font_color="#555")
        fig.update_layout(**plot_theme, title_text=target, title_font_color="#fff",
                          yaxis_title="%", xaxis_title="year")
        st.plotly_chart(fig, use_container_width=True)

        # show min/max/avg stats below chart
        s1, s2, s3 = st.columns(3)
        s1.markdown(f"<div class='metric-card'><div class='label'>average</div><div class='value' style='font-size:1.4rem'>{df[target].mean():.2f}%</div></div>", unsafe_allow_html=True)
        s2.markdown(f"<div class='metric-card'><div class='label'>peak</div><div class='value' style='font-size:1.4rem;color:#22c55e'>{df[target].max():.2f}%</div></div>", unsafe_allow_html=True)
        s3.markdown(f"<div class='metric-card'><div class='label'>lowest</div><div class='value' style='font-size:1.4rem;color:#ef4444'>{df[target].min():.2f}%</div></div>", unsafe_allow_html=True)

st.divider()

# ── section 3: predict future ─────────────────────────────────────────────────
st.markdown("<div class='section-title'>Predict <span>Future Outcomes</span></div>", unsafe_allow_html=True)
st.markdown("<div class='tab-hint'>enter your own commodity prices to predict what happens to the economy</div>", unsafe_allow_html=True)

commodity_info = {
    "WTI":             ("🛢 WTI Oil",         "$/barrel", means.get("WTI", 70.0)),
    "BRENT":           ("🛢 Brent Crude",      "$/barrel", means.get("BRENT", 75.0)),
    "NATURAL_GAS":     ("🔥 Natural Gas",      "$/mmbtu",  means.get("NATURAL_GAS", 3.5)),
    "ALUMINUM":        ("🔩 Aluminum",         "$/tonne",  means.get("ALUMINUM", 2000.0)),
    "CORN":            ("🌽 Corn",             "$/bushel", means.get("CORN", 280.0)),
    "COTTON":          ("🌿 Cotton",           "cents/lb", means.get("COTTON", 80.0)),
    "SUGAR":           ("🍬 Sugar",            "cents/lb", means.get("SUGAR", 18.0)),
    "COFFEE":          ("☕ Coffee",           "cents/lb", means.get("COFFEE", 180.0)),
    "COPPER":          ("🪙 Copper",           "$/tonne",  means.get("COPPER", 7000.0)),
    "WHEAT":           ("🌾 Wheat",            "$/bushel", means.get("WHEAT", 280.0)),
    "ALL_COMMODITIES": ("📦 All Commodities",  "index",    means.get("ALL_COMMODITIES", 150.0)),
}

user_inputs = {}
feature_list = [f for f in features if f in commodity_info]
rows = [feature_list[i:i+3] for i in range(0, len(feature_list), 3)]

for row in rows:
    cols = st.columns(3)
    for i, feat in enumerate(row):
        label, unit, default = commodity_info[feat]
        with cols[i]:
            user_inputs[feat] = st.number_input(
                f"{label} ({unit})", min_value=0.0,
                value=float(round(default, 2)), step=0.1, format="%.2f", key=feat
            )

st.markdown("<br>", unsafe_allow_html=True)
c1, c2 = st.columns([3, 1])
with c1:
    scenario = st.text_input("scenario name", value="my_scenario")
with c2:
    st.markdown("<br>", unsafe_allow_html=True)
    predict_btn = st.button("🔮 Predict Impact")

st.divider()

# ── results ───────────────────────────────────────────────────────────────────
if predict_btn:
    input_df = pd.DataFrame([user_inputs])[features]
    prediction = model.predict(input_df)[0]
    result = dict(zip(targets, prediction))

    mean_df = pd.DataFrame([{f: means.get(f, user_inputs[f]) for f in features}])
    baseline = dict(zip(targets, model.predict(mean_df)[0]))

    st.markdown(f"<div class='section-title'>Results — <span>{scenario}</span></div>", unsafe_allow_html=True)

    res_cols = st.columns(len(targets))
    for i, (target, value) in enumerate(result.items()):
        diff = value - baseline[target]
        arrow = "↑" if diff > 0 else "↓"
        color = "#ef4444" if diff > 0 and target != "GDP Growth (% Annual)" else "#22c55e"
        with res_cols[i]:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='label'>{icons.get(target,"")} {target}</div>
                <div class='value'>{value:.2f}%</div>
                <div class='sub' style='color:{color}'>{arrow} {abs(diff):.2f}% vs baseline</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # your scenario vs baseline chart — one tab per indicator
    st.markdown("<div class='section-title'>Your Scenario <span>vs Baseline</span></div>", unsafe_allow_html=True)
    result_tabs = st.tabs([f"{icons.get(t,'')} {t.split('(')[0].strip()}" for t in targets])
    for i, (tab, target) in enumerate(zip(result_tabs, targets)):
        with tab:
            fig = go.Figure()
            fig.add_trace(go.Bar(name="baseline", x=["baseline"], y=[baseline[target]],
                                 marker_color="#2a1a4a", marker_line_color="#7c3aed", marker_line_width=1.5, width=0.3))
            fig.add_trace(go.Bar(name="your scenario", x=["your scenario"], y=[result[target]],
                                 marker_color="#a855f7", width=0.3))
            fig.update_layout(**plot_theme, yaxis_title="%", showlegend=True)
            st.plotly_chart(fig, use_container_width=True)

    # save all outputs
    os.makedirs(RESULTS_DIR, exist_ok=True)
    out = {"inputs": user_inputs, "predictions": result, "baseline": baseline}
    json.dump(out, open(os.path.join(RESULTS_DIR, f"{scenario}_prediction.json"), "w"), indent=2)
    st.success(f"saved to output/results/{scenario}_prediction.json")

else:
    st.markdown("<div style='text-align:center;color:#444;padding:2rem;'>👆 enter commodity prices above and hit predict</div>", unsafe_allow_html=True)

# ── saved scenarios ───────────────────────────────────────────────────────────
st.divider()
st.markdown("<div class='section-title'>Saved <span>Scenarios</span></div>", unsafe_allow_html=True)
files = [f for f in os.listdir(RESULTS_DIR) if f.endswith("_prediction.json")] if os.path.exists(RESULTS_DIR) else []
if files:
    rows_data = []
    for f in files:
        name = f.replace("_prediction.json", "")
        data = json.load(open(os.path.join(RESULTS_DIR, f)))
        row = {"scenario": name}
        row.update(data["predictions"])  # all 4 macro outputs always saved
        row.update({f"↳ {k}": round(v, 2) for k, v in data["inputs"].items()})
        rows_data.append(row)
    st.dataframe(pd.DataFrame(rows_data), use_container_width=True)
else:
    st.markdown("<div style='color:#444;'>no saved scenarios yet — run a prediction above</div>", unsafe_allow_html=True)