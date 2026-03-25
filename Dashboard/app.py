import os, json, pickle, sys
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import yfinance as yf

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from business_profiles import BUSINESS_PROFILES, ALL_COMMODITIES, get_all_profiles
from business_translator import translate, calculate_cost_impact

DATA_DIR    = os.path.join(os.path.dirname(__file__), "..", "data")
MODEL_DIR   = os.path.join(os.path.dirname(__file__), "..", "models")
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "output", "results")

st.set_page_config(page_title="BizShock Analyzer", page_icon="📉", layout="wide")

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
.hero p { color: #888; font-size: 1rem; max-width: 520px; margin: 0.5rem auto 0; position: relative; z-index: 1; }

.card {
    background: #111; border: 1px solid #222;
    border-radius: 16px; padding: 1.5rem; margin-bottom: 1rem;
}
.card:hover { border-color: #7c3aed; transition: border-color 0.2s; }

.metric-card {
    background: linear-gradient(135deg, #111 60%, #1a0a2e);
    border: 1px solid #2a1a4a; border-radius: 16px;
    padding: 1.5rem; text-align: center; margin-bottom: 1rem;
}
.metric-card .label { color: #888; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; }
.metric-card .value { font-family: 'Syne', sans-serif; font-size: 2rem; font-weight: 700; color: #a855f7; margin: 0.3rem 0; }
.metric-card .sub { color: #555; font-size: 0.78rem; }

.verdict-card {
    border-radius: 16px; padding: 1.5rem; margin: 1rem 0;
    border: 1px solid #2a1a4a;
    background: linear-gradient(135deg, #111 60%, #1a0a2e);
}
.verdict-title { font-family: 'Syne', sans-serif; font-size: 1.6rem; font-weight: 800; margin-bottom: 0.5rem; }
.verdict-sub { color: #888; font-size: 0.9rem; }

.insight { padding: 0.6rem 1rem; margin: 0.4rem 0; border-radius: 8px; background: #111; border: 1px solid #1e1e1e; font-size: 0.9rem; }
.action { padding: 0.6rem 1rem; margin: 0.4rem 0; border-radius: 8px; background: #0d0d1a; border: 1px solid #2a1a4a; font-size: 0.9rem; }

.section-title { font-family: 'Syne', sans-serif; font-size: 1.4rem; font-weight: 700; color: #fff; margin: 2rem 0 0.5rem; }
.section-title span { color: #a855f7; }
.hint { color: #555; font-size: 0.82rem; margin-bottom: 1rem; }

hr { border-color: #1e1e1e !important; }

.stButton > button {
    background: linear-gradient(135deg, #7c3aed, #a855f7) !important;
    color: white !important; border: none !important; border-radius: 8px !important;
    font-family: 'Syne', sans-serif !important; font-weight: 600 !important;
    padding: 0.6rem 1.5rem !important; width: 100%;
}
.stTabs [data-baseweb="tab-list"] { background: #111; border-radius: 12px; padding: 4px; gap: 4px; border: 1px solid #222; }
.stTabs [data-baseweb="tab"] { background: transparent; color: #666; border-radius: 8px; font-family: 'Syne', sans-serif; font-weight: 600; }
.stTabs [aria-selected="true"] { background: linear-gradient(135deg, #7c3aed, #a855f7) !important; color: white !important; }
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── load model ────────────────────────────────────────────────────────────────
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

@st.cache_data(ttl=300)  # refresh live prices every 5 mins
def fetch_live_price(ticker):
    try:
        price = yf.Ticker(ticker).history(period="1d")["Close"].iloc[-1]
        return round(float(price), 2)
    except:
        return None

model, features, targets = load_model()
df = load_history()
historical_means = df[features].mean().to_dict()

if model is None:
    st.error("model not found — run ml_model.py first")
    st.stop()

plot_theme = dict(
    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    font_color="#888", xaxis=dict(gridcolor="#1e1e1e", color="#555"),
    yaxis=dict(gridcolor="#1e1e1e", color="#555"),
    margin=dict(t=40, b=20), legend=dict(bgcolor="rgba(0,0,0,0)", font_color="#aaa")
)

# ── hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>BizShock.<br>Analyzer.</h1>
    <p>understand how global commodity price shocks affect your business — powered by live market data and machine learning</p>
</div>
""", unsafe_allow_html=True)

st.divider()

# ── sidebar: business setup ───────────────────────────────────────────────────
st.sidebar.markdown("<h2 style='font-family:Syne;color:#fff;'>🏪 Your Business</h2>", unsafe_allow_html=True)

business_type = st.sidebar.selectbox("what kind of business?", get_all_profiles())
profile = BUSINESS_PROFILES[business_type]
st.sidebar.caption(profile["description"])
st.sidebar.divider()

scenario_name = st.sidebar.text_input("scenario name", value="my_scenario")
analyze_btn = st.sidebar.button("🔮 Analyze My Business")

# ── step 1: build commodity basket ───────────────────────────────────────────
st.markdown("<div class='section-title'>Step 1 — <span>Your Cost Basket</span></div>", unsafe_allow_html=True)
st.markdown("<div class='hint'>these are the commodities that affect your business costs — adjust weights to match your actual cost structure</div>", unsafe_allow_html=True)

if business_type == "🛠 Custom":
    st.markdown("<div class='hint'>add as many commodities as you want and set their weight in your cost structure</div>", unsafe_allow_html=True)

    if "custom_commodities" not in st.session_state:
        st.session_state.custom_commodities = [{"name": "Crude Oil", "weight": 50}]

    for i, row in enumerate(st.session_state.custom_commodities):
        c1, c2, c3 = st.columns([3, 2, 1])
        with c1:
            name = st.selectbox("commodity", list(ALL_COMMODITIES.keys()), key=f"name_{i}",
                                index=list(ALL_COMMODITIES.keys()).index(row["name"]) if row["name"] in ALL_COMMODITIES else 0)
            st.session_state.custom_commodities[i]["name"] = name
        with c2:
            weight = st.number_input("weight %", 0, 100, row["weight"], key=f"weight_{i}")
            st.session_state.custom_commodities[i]["weight"] = weight
        with c3:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("✕", key=f"remove_{i}") and len(st.session_state.custom_commodities) > 1:
                st.session_state.custom_commodities.pop(i)
                st.rerun()

    if st.button("+ Add Commodity"):
        st.session_state.custom_commodities.append({"name": "Wheat", "weight": 10})
        st.rerun()

    total_weight = sum(r["weight"] for r in st.session_state.custom_commodities)
    if total_weight != 100:
        st.warning(f"weights add up to {total_weight}% — should be 100%")

    # build profile commodities from custom input
    active_commodities = {}
    for row in st.session_state.custom_commodities:
        com = ALL_COMMODITIES.get(row["name"])
        if com:
            key = row["name"].upper().replace(" ", "_")
            active_commodities[key] = {"ticker": com["ticker"], "weight": row["weight"] / 100}

else:
    active_commodities = profile["commodities"]
    cols = st.columns(len(active_commodities))
    for i, (commodity, info) in enumerate(active_commodities.items()):
        with cols[i]:
            new_weight = st.number_input(
                f"{commodity}", 0, 100,
                int(info["weight"] * 100),
                key=f"w_{commodity}"
            )
            active_commodities[commodity]["weight"] = new_weight / 100

st.divider()

# ── step 2: live prices ───────────────────────────────────────────────────────
st.markdown("<div class='section-title'>Step 2 — <span>Live Market Prices</span></div>", unsafe_allow_html=True)
st.markdown("<div class='hint'>fetched live from markets — updates every 5 minutes</div>", unsafe_allow_html=True)

live_prices = {}
price_cols = st.columns(len(active_commodities))
for i, (commodity, info) in enumerate(active_commodities.items()):
    price = fetch_live_price(info["ticker"])
    live_prices[commodity] = price
    hist = historical_means.get(commodity, 0)
    change = ((price - hist) / hist * 100) if price and hist else 0
    arrow = "↑" if change > 0 else "↓"
    color = "#ef4444" if change > 0 else "#22c55e"
    with price_cols[i]:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='label'>{commodity.replace('_',' ')}</div>
            <div class='value'>${price:.2f}</div>
            <div class='sub' style='color:{color}'>{arrow} {abs(change):.1f}% vs hist avg</div>
        </div>""", unsafe_allow_html=True)

st.divider()

# ── step 3: macro chart explorer ─────────────────────────────────────────────
st.markdown("<div class='section-title'>Step 3 — <span>Historical Macro Trends</span></div>", unsafe_allow_html=True)
st.markdown("<div class='hint'>explore how macro indicators have moved over the years</div>", unsafe_allow_html=True)

icons = {"Inflation (CPI %)": "📈", "GDP Growth (% Annual)": "📊", "Unemployment Rate (%)": "👷", "Interest Rate (Real, %)": "🏦"}
tab_labels = [f"{icons.get(t,'')} {t.split('(')[0].strip()}" for t in targets]
tabs = st.tabs(tab_labels)

for tab, target in zip(tabs, targets):
    with tab:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df.index, y=df[target], mode="lines+markers",
            line=dict(color="#a855f7", width=2.5),
            marker=dict(size=5, color="#7c3aed"),
            fill="tozeroy", fillcolor="rgba(120,40,255,0.08)"
        ))
        avg = df[target].mean()
        fig.add_hline(y=avg, line_dash="dash", line_color="#444",
                      annotation_text=f"avg {avg:.2f}%", annotation_font_color="#555")
        fig.update_layout(**plot_theme, title_text=target, title_font_color="#fff", yaxis_title="%")
        st.plotly_chart(fig, use_container_width=True)

        s1, s2, s3 = st.columns(3)
        s1.markdown(f"<div class='metric-card'><div class='label'>average</div><div class='value' style='font-size:1.3rem'>{df[target].mean():.2f}%</div></div>", unsafe_allow_html=True)
        s2.markdown(f"<div class='metric-card'><div class='label'>peak</div><div class='value' style='font-size:1.3rem;color:#22c55e'>{df[target].max():.2f}%</div></div>", unsafe_allow_html=True)
        s3.markdown(f"<div class='metric-card'><div class='label'>lowest</div><div class='value' style='font-size:1.3rem;color:#ef4444'>{df[target].min():.2f}%</div></div>", unsafe_allow_html=True)

st.divider()

# ── step 4: analysis results ──────────────────────────────────────────────────
if analyze_btn:
    # build model input using live prices, fallback to historical mean
    input_data = {f: live_prices.get(f, historical_means.get(f, 0)) for f in features}
    input_df = pd.DataFrame([input_data])[features]
    prediction = model.predict(input_df)[0]
    result = dict(zip(targets, prediction))

    # baseline using historical means
    baseline_df = pd.DataFrame([{f: historical_means.get(f, 0) for f in features}])
    baseline = dict(zip(targets, model.predict(baseline_df)[0]))

    # cost impact
    cost_impact, breakdown = calculate_cost_impact(active_commodities, live_prices, historical_means)

    # translation
    translation = translate(result, business_type, cost_impact)
    verdict_text, verdict_desc, verdict_color = translation["verdict"]

    st.markdown(f"<div class='section-title'>Step 4 — <span>Your Business Analysis</span></div>", unsafe_allow_html=True)

    # verdict
    st.markdown(f"""
    <div class='verdict-card'>
        <div class='verdict-title' style='color:{verdict_color}'>{verdict_text}</div>
        <div class='verdict-sub'>{verdict_desc}</div>
    </div>""", unsafe_allow_html=True)

    # macro predictions
    st.markdown("<div class='section-title'>Predicted <span>Macro Indicators</span></div>", unsafe_allow_html=True)
    res_cols = st.columns(len(targets))
    for i, (target, value) in enumerate(result.items()):
        diff = value - baseline[target]
        arrow = "↑" if diff > 0 else "↓"
        color = "#ef4444" if diff > 0 and target != "GDP Growth (% Annual)" else "#22c55e"
        with res_cols[i]:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='label'>{icons.get(target,'')} {target}</div>
                <div class='value'>{value:.2f}%</div>
                <div class='sub' style='color:{color}'>{arrow} {abs(diff):.2f}% vs baseline</div>
            </div>""", unsafe_allow_html=True)

    # cost breakdown
    st.markdown("<div class='section-title'>Your <span>Cost Impact Breakdown</span></div>", unsafe_allow_html=True)
    if breakdown:
        bd_df = pd.DataFrame(breakdown).T.reset_index()
        bd_df.columns = ["commodity", "live price", "hist avg", "change %", "weight", "weighted impact %"]
        st.dataframe(bd_df, use_container_width=True)
        st.markdown(f"**Total estimated cost impact on your business: {'🔴' if cost_impact > 10 else '🟡' if cost_impact > 0 else '🟢'} {cost_impact:+.1f}%**")

    # vs baseline chart
    st.markdown("<div class='section-title'>Your Scenario <span>vs Baseline</span></div>", unsafe_allow_html=True)
    fig = go.Figure()
    fig.add_trace(go.Bar(name="historical baseline", x=targets, y=[baseline[t] for t in targets],
                         marker_color="#2a1a4a", marker_line_color="#7c3aed", marker_line_width=1.5))
    fig.add_trace(go.Bar(name="current prediction", x=targets, y=[result[t] for t in targets],
                         marker_color="#a855f7"))
    fig.update_layout(**plot_theme, barmode="group", yaxis_title="%")
    st.plotly_chart(fig, use_container_width=True)

    # insights
    st.markdown("<div class='section-title'>💡 <span>What This Means for You</span></div>", unsafe_allow_html=True)
    for insight in translation["insights"]:
        st.markdown(f"<div class='insight'>{insight}</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-title'>✅ <span>What You Should Do</span></div>", unsafe_allow_html=True)
    for action in translation["actions"]:
        st.markdown(f"<div class='action'>{action}</div>", unsafe_allow_html=True)

    # save
    os.makedirs(RESULTS_DIR, exist_ok=True)
    out = {
        "business": business_type,
        "scenario": scenario_name,
        "live_prices": live_prices,
        "predictions": result,
        "baseline": baseline,
        "cost_impact_pct": cost_impact,
        "verdict": verdict_text
    }
    json.dump(out, open(os.path.join(RESULTS_DIR, f"{scenario_name}_prediction.json"), "w"), indent=2)
    st.success(f"saved to output/results/{scenario_name}_prediction.json")

else:
    st.markdown("<div style='text-align:center;color:#444;padding:2rem;'>👈 select your business type and hit Analyze My Business</div>", unsafe_allow_html=True)

# ── saved scenarios ───────────────────────────────────────────────────────────
st.divider()
st.markdown("<div class='section-title'>Saved <span>Scenarios</span></div>", unsafe_allow_html=True)
files = [f for f in os.listdir(RESULTS_DIR) if f.endswith("_prediction.json")] if os.path.exists(RESULTS_DIR) else []
if files:
    rows = []
    for f in files:
        data = json.load(open(os.path.join(RESULTS_DIR, f)))
        row = {"scenario": data.get("scenario",""), "business": data.get("business",""), "verdict": data.get("verdict",""), "cost_impact_%": data.get("cost_impact_pct",0)}
        row.update(data.get("predictions", {}))
        rows.append(row)
    st.dataframe(pd.DataFrame(rows), use_container_width=True)
else:
    st.markdown("<div style='color:#444;'>no saved scenarios yet</div>", unsafe_allow_html=True)