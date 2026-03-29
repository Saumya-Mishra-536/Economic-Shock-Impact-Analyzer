import os, json, pickle, sys
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import yfinance as yf

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from business_profiles import BUSINESS_PROFILES, ALL_COMMODITIES, get_all_profiles
from business_translator import translate, calculate_cost_impact

DATA_DIR    = os.path.join(os.path.dirname(__file__), "..", "data")
MODEL_DIR   = os.path.join(os.path.dirname(__file__), "..", "models")
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "output", "results")

st.set_page_config(page_title="BizShock", page_icon="📉", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=IBM+Plex+Mono:wght@300;400;500&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

:root {
    --bg:       #080a0f;
    --surface:  #0d1117;
    --border:   #1c2333;
    --border2:  #2a3444;
    --text:     #c9d1d9;
    --muted:    #484f58;
    --accent:   #58a6ff;
    --green:    #3fb950;
    --red:      #f85149;
    --yellow:   #d29922;
    --purple:   #bc8cff;
}

* { font-family: 'IBM Plex Sans', sans-serif; box-sizing: border-box; }
.stApp { background: var(--bg); color: var(--text); }
[data-testid="stSidebar"] {
    background: var(--surface);
    border-right: 1px solid var(--border);
}

/* hide streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }

/* topbar */
.topbar {
    display: flex; align-items: center; justify-content: space-between;
    padding: 1.2rem 0 1rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 2rem;
}
.topbar-left { display: flex; align-items: baseline; gap: 1rem; }
.logo {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 2.2rem; letter-spacing: 0.08em;
    color: #fff;
}
.logo span { color: var(--accent); margin-left: 0.2rem; }
.tagline { font-family: 'IBM Plex Mono', monospace; font-size: 0.7rem; color: var(--muted); letter-spacing: 0.05em; }
.tagline { word-spacing: 0.12em; }
.live-badge {
    font-family: 'IBM Plex Mono', monospace; font-size: 0.65rem;
    background: rgba(63,185,80,0.1); border: 1px solid rgba(63,185,80,0.3);
    color: var(--green); padding: 0.2rem 0.6rem; border-radius: 4px;
    letter-spacing: 0.08em;
}

/* section headers */
.sec-header {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem; font-weight: 500;
    color: var(--muted); letter-spacing: 0.15em;
    text-transform: uppercase;
    border-bottom: 1px solid var(--border);
    padding-bottom: 0.5rem; margin: 2rem 0 1rem;
    display: flex; align-items: center; gap: 0.5rem;
}
.sec-header::before {
    content: ''; display: inline-block;
    width: 6px; height: 6px;
    background: var(--accent); border-radius: 50%;
}

/* metric cards */
.mcard {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 6px; padding: 1.2rem 1.4rem;
    position: relative; overflow: hidden;
}
.mcard::after {
    content: ''; position: absolute;
    top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, var(--accent), transparent);
}
.mcard .mlabel {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.6rem; color: var(--muted);
    letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 0.4rem;
}
.mcard .mvalue {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 2.4rem; color: #fff; line-height: 1; margin-bottom: 0.3rem;
}
.mcard .msub {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem; color: var(--muted);
}
.mcard.up::after { background: linear-gradient(90deg, var(--red), transparent); }
.mcard.down::after { background: linear-gradient(90deg, var(--green), transparent); }
.mcard.neutral::after { background: linear-gradient(90deg, var(--purple), transparent); }

/* price ticker cards */
.pcard {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 6px; padding: 1rem 1.2rem;
}
.pcard .pname { font-family: 'IBM Plex Mono', monospace; font-size: 0.6rem; color: var(--muted); letter-spacing: 0.1em; text-transform: uppercase; }
.pcard .pprice { font-family: 'Bebas Neue', sans-serif; font-size: 1.8rem; color: #fff; }
.pcard .pchange { font-family: 'IBM Plex Mono', monospace; font-size: 0.65rem; }

/* verdict */
.verdict {
    background: var(--surface); border: 1px solid var(--border2);
    border-radius: 6px; padding: 1.8rem;
    display: flex; align-items: flex-start; gap: 1.5rem;
    margin: 1rem 0;
}
.verdict-icon { font-size: 2rem; line-height: 1; }
.verdict-title { font-family: 'Bebas Neue', sans-serif; font-size: 1.8rem; letter-spacing: 0.05em; margin-bottom: 0.3rem; }
.verdict-desc { font-size: 0.85rem; color: var(--muted); line-height: 1.5; }

/* insight / action rows */
.insight-row {
    display: flex; align-items: flex-start; gap: 0.8rem;
    padding: 0.8rem 1rem; margin: 0.3rem 0;
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 6px; font-size: 0.85rem; line-height: 1.5;
}
.insight-row .tag {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.55rem; letter-spacing: 0.1em;
    padding: 0.15rem 0.4rem; border-radius: 3px;
    white-space: nowrap; margin-top: 0.1rem;
}
.tag-red { background: rgba(248,81,73,0.15); color: var(--red); border: 1px solid rgba(248,81,73,0.3); }
.tag-yellow { background: rgba(210,153,34,0.15); color: var(--yellow); border: 1px solid rgba(210,153,34,0.3); }
.tag-green { background: rgba(63,185,80,0.15); color: var(--green); border: 1px solid rgba(63,185,80,0.3); }

.action-row {
    display: flex; align-items: flex-start; gap: 0.8rem;
    padding: 0.8rem 1rem; margin: 0.3rem 0;
    background: rgba(88,166,255,0.04); border: 1px solid rgba(88,166,255,0.15);
    border-radius: 6px; font-size: 0.85rem; line-height: 1.5; color: var(--text);
}
.action-num {
    font-family: 'IBM Plex Mono', monospace; font-size: 0.6rem;
    color: var(--accent); min-width: 1.2rem;
    margin-top: 0.15rem;
}

/* number inputs */
.stNumberInput input {
    background: var(--surface) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 4px !important; color: var(--text) !important;
    font-family: 'IBM Plex Mono', monospace !important;
}
.stNumberInput input:focus { border-color: var(--accent) !important; }

/* selectbox */
.stSelectbox > div > div {
    background: var(--surface) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 4px !important;
}

/* button */
.stButton > button {
    background: var(--accent) !important; color: #000 !important;
    border: none !important; border-radius: 4px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.75rem !important; font-weight: 500 !important;
    letter-spacing: 0.08em !important; text-transform: uppercase !important;
    padding: 0.6rem 1.5rem !important; width: 100% !important;
}
.stButton > button:hover { opacity: 0.85 !important; }

/* tabs */
.stTabs [data-baseweb="tab-list"] {
    background: var(--surface); border-radius: 4px;
    padding: 3px; gap: 2px; border: 1px solid var(--border);
}
.stTabs [data-baseweb="tab"] {
    background: transparent; color: var(--muted);
    border-radius: 3px;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.7rem !important; letter-spacing: 0.05em;
}
.stTabs [aria-selected="true"] {
    background: var(--accent) !important; color: #000 !important;
}

/* sidebar */
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stTextInput label {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.65rem !important; color: var(--muted) !important;
    letter-spacing: 0.1em; text-transform: uppercase;
}

hr { border-color: var(--border) !important; }

/* dataframe */
.stDataFrame { border: 1px solid var(--border) !important; border-radius: 6px !important; }
</style>
""", unsafe_allow_html=True)

# ── load ──────────────────────────────────────────────────────────────────────
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

@st.cache_data(ttl=180)
def fetch_live_price(ticker):
    """Return latest trade/close for a Yahoo ticker with robust fallbacks.

    Strategy:
    1) Try fast_info.last_price (fast + works for many futures).
    2) Fallback to history over wider windows (5d → 1mo → 3mo) and take last non‑NA close.
    3) Final fallback to yf.download.
    Returns None only if all attempts fail.
    """
    try:
        t = yf.Ticker(ticker)
        # 1) fast_info
        fi = getattr(t, "fast_info", None)
        if fi is not None:
            last = getattr(fi, "last_price", None)
            if last is None:
                try:
                    last = fi.get("last_price")  # dict-like in some yfinance versions
                except Exception:
                    last = None
            if last is not None and not pd.isna(last) and float(last) != 0:
                return round(float(last), 2)

        # 2) history with broader windows
        for period in ("5d", "1mo", "3mo"):
            df = t.history(period=period, interval="1d", auto_adjust=False, prepost=True, actions=False)
            if df is not None and not df.empty and "Close" in df.columns:
                s = df["Close"].dropna()
                if not s.empty:
                    return round(float(s.iloc[-1]), 2)

        # 3) yf.download as a last resort
        df2 = yf.download(ticker, period="5d", interval="1d", progress=False)
        if df2 is not None and not df2.empty and "Close" in df2.columns:
            s2 = df2["Close"].dropna()
            if not s2.empty:
                return round(float(s2.iloc[-1]), 2)
    except Exception:
        pass
    return None

model, features, targets = load_model()
df = load_history()
historical_means = df[features].mean().to_dict()

if model is None:
    st.error("model not found — run ml_model.py first")
    st.stop()

plot_theme = dict(
    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    font=dict(family="IBM Plex Mono", color="#484f58", size=11),
    xaxis=dict(gridcolor="#1c2333", color="#484f58", linecolor="#1c2333"),
    yaxis=dict(gridcolor="#1c2333", color="#484f58", linecolor="#1c2333"),
    margin=dict(t=40, b=20, l=10, r=10),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#484f58", size=10))
)

# ── topbar ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="topbar">
    <div class="topbar-left">
        <div class="logo">Biz<span> Shock</span></div>
        <div class="tagline">COMMODITY SHOCK · BUSINESS IMPACT ANALYZER</div>
    </div>
    <div class="live-badge">● LIVE DATA</div>
</div>
""", unsafe_allow_html=True)

# ── sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.markdown("""
<div style='font-family:"IBM Plex Mono",monospace;font-size:0.6rem;color:#484f58;
letter-spacing:0.15em;text-transform:uppercase;border-bottom:1px solid #1c2333;
padding-bottom:0.8rem;margin-bottom:1rem'>
▸ Business Configuration
</div>""", unsafe_allow_html=True)

business_type = st.sidebar.selectbox("Business Type", get_all_profiles(), label_visibility="visible")
profile = BUSINESS_PROFILES[business_type]
st.sidebar.markdown(f"<div style='font-family:IBM Plex Mono,monospace;font-size:0.65rem;color:#484f58;margin:-0.5rem 0 1rem'>{profile['description']}</div>", unsafe_allow_html=True)
st.sidebar.divider()
scenario_name = st.sidebar.text_input("Scenario ID", value="scenario_01")
analyze_btn = st.sidebar.button("▶ RUN ANALYSIS")

# ── step 1: cost basket ───────────────────────────────────────────────────────
st.markdown("<div class='sec-header'>01 — Cost Basket Configuration</div>", unsafe_allow_html=True)

if business_type == "🛠 Custom":
    if "custom_commodities" not in st.session_state:
        st.session_state.custom_commodities = [{"name": "Crude Oil", "weight": 50}]

    for i, row in enumerate(st.session_state.custom_commodities):
        c1, c2, c3 = st.columns([3, 2, 1])
        with c1:
            name = st.selectbox("Commodity", list(ALL_COMMODITIES.keys()), key=f"name_{i}",
                                index=list(ALL_COMMODITIES.keys()).index(row["name"]) if row["name"] in ALL_COMMODITIES else 0)
            st.session_state.custom_commodities[i]["name"] = name
        with c2:
            weight = st.number_input("Weight %", 0, 100, row["weight"], key=f"weight_{i}")
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
    color = "#3fb950" if total_weight == 100 else "#f85149"
    st.markdown(f"<div style='font-family:IBM Plex Mono,monospace;font-size:0.7rem;color:{color}'>Total weight: {total_weight}% {'✓' if total_weight==100 else '— must equal 100%'}</div>", unsafe_allow_html=True)

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
            new_weight = st.number_input(commodity.replace("_"," "), 0, 100, int(info["weight"]*100), key=f"w_{commodity}")
            active_commodities[commodity]["weight"] = new_weight / 100

# ── step 2: live prices ───────────────────────────────────────────────────────
st.markdown("<div class='sec-header'>02 — Live Market Data</div>", unsafe_allow_html=True)

live_prices = {}
price_cols = st.columns(len(active_commodities))
for i, (commodity, info) in enumerate(active_commodities.items()):
    price = fetch_live_price(info["ticker"])
    live_prices[commodity] = price
    hist = historical_means.get(commodity, 0)

    if price is None:
        price_text = "N/A"
        change_text = "no live data"
        tag_color = "#484f58"  # muted
    else:
        price_text = f"${price:.2f}"
        if hist:
            change = ((price - hist) / hist * 100)
            tag_color = "#f85149" if change > 5 else "#d29922" if change > 0 else "#3fb950"
            arrow = "▲" if change > 0 else "▼"
            change_text = f"{arrow} {abs(change):.1f}% vs hist avg"
        else:
            # No historical baseline; show price only
            tag_color = "#484f58"
            change_text = "baseline N/A"

    with price_cols[i]:
        st.markdown(f"""
        <div class='pcard'>
            <div class='pname'>{commodity.replace('_',' ')}</div>
            <div class='pprice'>{price_text}</div>
            <div class='pchange' style='color:{tag_color}'>{change_text}</div>
        </div>""", unsafe_allow_html=True)

# ── step 3: macro explorer ────────────────────────────────────────────────────
st.markdown("<div class='sec-header'>03 — Historical Macro Indicators</div>", unsafe_allow_html=True)

# Tab titles without abbreviations (use full names)
tabs = st.tabs([t.split('(')[0].strip() for t in targets])

for tab, target in zip(tabs, targets):
    with tab:
        fig = go.Figure()
        series = df[target]
        ymin, ymax = float(series.min()), float(series.max())

        # main line
        fig.add_trace(go.Scatter(
            x=df.index, y=series, mode="lines",
            line=dict(color="#58a6ff", width=1.5),
            name=target
        ))
        # small markers for context
        fig.add_trace(go.Scatter(
            x=df.index, y=series, mode="markers",
            marker=dict(size=4, color="#58a6ff", line=dict(color="#0d1117", width=1)),
            showlegend=False
        ))

        # Average band highlights: green below avg, red above avg
        avg = float(series.mean())
        fig.add_hrect(y0=ymin, y1=avg, fillcolor="rgba(63,185,80,0.06)", line_width=0, layer="below")
        fig.add_hrect(y0=avg, y1=ymax, fillcolor="rgba(248,81,73,0.06)", line_width=0, layer="below")

        # Mean reference line
        fig.add_hline(y=avg, line_dash="dot", line_color="#2a3444", line_width=1,
                      annotation_text=f"μ {avg:.2f}%",
                      annotation_font=dict(color="#484f58", size=10, family="IBM Plex Mono"))

        # Emphasize the latest point
        last_x = series.index[-1]
        last_y = float(series.iloc[-1])
        fig.add_trace(
            go.Scatter(x=[last_x], y=[last_y], mode="markers",
                       marker=dict(size=8, color="#58a6ff", line=dict(color="#ffffff", width=1.5)),
                       showlegend=False, hoverinfo="skip")
        )
        fig.update_layout(**plot_theme, height=280)
        st.plotly_chart(fig, use_container_width=True)

        s1, s2, s3, s4 = st.columns(4)
        stats = [
            ("AVG", f"{df[target].mean():.2f}%", "neutral"),
            ("PEAK", f"{df[target].max():.2f}%", "up"),
            ("LOW", f"{df[target].min():.2f}%", "down"),
            ("LATEST", f"{df[target].iloc[-1]:.2f}%", "neutral"),
        ]
        for col, (label, val, cls) in zip([s1,s2,s3,s4], stats):
            col.markdown(f"""
            <div class='mcard {cls}'>
                <div class='mlabel'>{label}</div>
                <div class='mvalue' style='font-size:1.6rem'>{val}</div>
            </div>""", unsafe_allow_html=True)

# ── step 4: analysis ──────────────────────────────────────────────────────────
st.markdown("<div class='sec-header'>04 — Business Impact Analysis</div>", unsafe_allow_html=True)

if analyze_btn:
    # Use live price when available; otherwise fall back to historical mean
    input_data  = {f: (live_prices.get(f) if live_prices.get(f) is not None else historical_means.get(f, 0)) for f in features}
    input_df    = pd.DataFrame([input_data])[features]
    prediction  = model.predict(input_df)[0]
    result      = dict(zip(targets, prediction))

    baseline_df = pd.DataFrame([{f: historical_means.get(f, 0) for f in features}])
    baseline    = dict(zip(targets, model.predict(baseline_df)[0]))

    cost_impact, breakdown = calculate_cost_impact(active_commodities, live_prices, historical_means)
    translation = translate(result, business_type, cost_impact)
    verdict_text, verdict_desc, verdict_color = translation["verdict"]

    # verdict
    verdict_icon = "🔴" if "Tough" in verdict_text else "🟡" if "Caution" in verdict_text else "🟢"
    st.markdown(f"""
    <div class='verdict'>
        <div class='verdict-icon'>{verdict_icon}</div>
        <div>
            <div class='verdict-title' style='color:{verdict_color}'>{verdict_text}</div>
            <div class='verdict-desc'>{verdict_desc}</div>
        </div>
    </div>""", unsafe_allow_html=True)

    # macro predictions
    st.markdown("<div style='font-family:IBM Plex Mono,monospace;font-size:0.6rem;color:#484f58;letter-spacing:0.12em;margin:1.5rem 0 0.8rem'>PREDICTED MACRO INDICATORS</div>", unsafe_allow_html=True)
    res_cols = st.columns(len(targets))
    for i, (target, value) in enumerate(result.items()):
        diff  = value - baseline[target]
        arrow = "▲" if diff > 0 else "▼"
        color = "#f85149" if diff > 0 and target != "GDP Growth (% Annual)" else "#3fb950"
        cls   = "up" if diff > 0 else "down"
        with res_cols[i]:
            st.markdown(f"""
            <div class='mcard {cls}'>
                <div class='mlabel'>{target.split("(")[0].strip()}</div>
                <div class='mvalue'>{value:.1f}%</div>
                <div class='msub' style='color:{color}'>{arrow} {abs(diff):.2f}pp vs baseline</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # cost breakdown + chart side by side
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown("<div style='font-family:IBM Plex Mono,monospace;font-size:0.6rem;color:#484f58;letter-spacing:0.12em;margin-bottom:0.8rem'>COST IMPACT BREAKDOWN</div>", unsafe_allow_html=True)
        if breakdown:
            bd_df = pd.DataFrame(breakdown).T.reset_index()
            bd_df.columns = ["commodity", "live $", "hist avg", "Δ%", "weight", "impact%"]
            st.dataframe(bd_df.style.format({"live $": "{:.2f}", "hist avg": "{:.2f}", "Δ%": "{:+.1f}", "weight": "{:.0%}", "impact%": "{:+.2f}"}), use_container_width=True, hide_index=True)
            color = "#f85149" if cost_impact > 10 else "#d29922" if cost_impact > 0 else "#3fb950"
            st.markdown(f"<div style='font-family:IBM Plex Mono,monospace;font-size:0.75rem;color:{color};margin-top:0.5rem'>TOTAL COST IMPACT: {cost_impact:+.1f}%</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown("<div style='font-family:IBM Plex Mono,monospace;font-size:0.6rem;color:#484f58;letter-spacing:0.12em;margin-bottom:0.8rem'>SCENARIO vs BASELINE</div>", unsafe_allow_html=True)
        fig = go.Figure()
        short = [t.split("(")[0].strip() for t in targets]
        fig.add_trace(go.Bar(name="baseline", x=short, y=[baseline[t] for t in targets],
                             marker_color="#1c2333", marker_line_color="#2a3444", marker_line_width=1))
        fig.add_trace(go.Bar(name="current", x=short, y=[result[t] for t in targets],
                             marker_color="#58a6ff", marker_line_color="#58a6ff", marker_line_width=0))
        fig.update_layout(**plot_theme, barmode="group", height=260)
        st.plotly_chart(fig, use_container_width=True)

    # insights
    st.markdown("<div style='font-family:IBM Plex Mono,monospace;font-size:0.6rem;color:#484f58;letter-spacing:0.12em;margin:1.5rem 0 0.6rem'>MARKET SIGNALS</div>", unsafe_allow_html=True)
    for insight in translation["insights"]:
        emoji = insight[0]
        tag = "RISK" if "🔴" in insight else "WATCH" if "🟡" in insight else "OK"
        tag_cls = "tag-red" if "🔴" in insight else "tag-yellow" if "🟡" in insight else "tag-green"
        text = insight[2:].strip()
        st.markdown(f"<div class='insight-row'><span class='tag {tag_cls}'>{tag}</span>{text}</div>", unsafe_allow_html=True)

    st.markdown("<div style='font-family:IBM Plex Mono,monospace;font-size:0.6rem;color:#484f58;letter-spacing:0.12em;margin:1.5rem 0 0.6rem'>RECOMMENDED ACTIONS</div>", unsafe_allow_html=True)
    for i, action in enumerate(translation["actions"], 1):
        text = action[2:].strip()
        st.markdown(f"<div class='action-row'><span class='action-num'>{i:02d}</span>{text}</div>", unsafe_allow_html=True)

    # save
    os.makedirs(RESULTS_DIR, exist_ok=True)
    out = {"business": business_type, "scenario": scenario_name, "live_prices": live_prices,
           "predictions": result, "baseline": baseline, "cost_impact_pct": cost_impact, "verdict": verdict_text}
    json.dump(out, open(os.path.join(RESULTS_DIR, f"{scenario_name}_prediction.json"), "w"), indent=2)
    st.markdown(f"<div style='font-family:IBM Plex Mono,monospace;font-size:0.65rem;color:#3fb950;margin-top:1rem'>✓ saved → output/results/{scenario_name}_prediction.json</div>", unsafe_allow_html=True)

else:
    st.markdown("""
    <div style='border:1px dashed #1c2333;border-radius:6px;padding:3rem;text-align:center;margin:1rem 0'>
        <div style='font-family:Bebas Neue,sans-serif;font-size:1.4rem;color:#2a3444;letter-spacing:0.1em'>
            SELECT YOUR BUSINESS TYPE AND RUN ANALYSIS
        </div>
        <div style='font-family:IBM Plex Mono,monospace;font-size:0.65rem;color:#2a3444;margin-top:0.5rem'>
            configure cost basket → fetch live prices → predict impact
        </div>
    </div>""", unsafe_allow_html=True)

# ── saved scenarios ───────────────────────────────────────────────────────────
st.markdown("<div class='sec-header'>05 — Saved Scenarios</div>", unsafe_allow_html=True)
files = [f for f in os.listdir(RESULTS_DIR) if f.endswith("_prediction.json")] if os.path.exists(RESULTS_DIR) else []
if files:
    rows = []
    for f in files:
        data = json.load(open(os.path.join(RESULTS_DIR, f)))
        row = {"scenario": data.get("scenario",""), "business": data.get("business",""),
               "verdict": data.get("verdict",""), "cost Δ%": data.get("cost_impact_pct",0)}
        row.update(data.get("predictions", {}))
        rows.append(row)
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
else:
    st.markdown("<div style='font-family:IBM Plex Mono,monospace;font-size:0.7rem;color:#2a3444;padding:1rem 0'>no saved scenarios — run an analysis above</div>", unsafe_allow_html=True)
