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

st.set_page_config(page_title="BizShock", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&family=Source+Sans+3:wght@300;400;500;600&family=IBM+Plex+Mono:wght@300;400;500&display=swap');

:root {
    --bg:         #09090e;
    --surface:    #0f1018;
    --surface2:   #14151f;
    --border:     #1e2030;
    --border2:    #2a2d44;
    --text:       #e2e4f0;
    --muted:      #5a5d7a;
    --muted2:     #3a3d55;
    --gold:       #c9a84c;
    --gold-light: #e8c97a;
    --gold-dim:   rgba(201,168,76,0.12);
    --green:      #3ecf8e;
    --red:        #f2655a;
    --amber:      #f0a23a;
    --blue:       #5b8ff9;
}

* { font-family: 'Source Sans 3', sans-serif; box-sizing: border-box; }
.stApp { background: var(--bg); color: var(--text); }

#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }
[data-testid="stSidebar"] { display: none; }
section[data-testid="stSidebarContent"] { display: none; }
.block-container { padding: 0 !important; max-width: 100% !important; }

.navbar {
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 3rem; height: 68px;
    background: var(--surface); border-bottom: 1px solid var(--border);
    position: sticky; top: 0; z-index: 100;
}
.nav-brand {
    font-family: 'Playfair Display', serif; font-size: 1.5rem;
    font-weight: 600; color: var(--gold); letter-spacing: 0.04em;
}
.nav-brand span { color: var(--text); font-weight: 400; }
.nav-tagline {
    font-family: 'IBM Plex Mono', monospace; font-size: 0.58rem;
    color: var(--muted); letter-spacing: 0.18em; text-transform: uppercase; margin-top: 2px;
}
.nav-steps { display: flex; gap: 2px; }
.nav-step {
    font-family: 'IBM Plex Mono', monospace; font-size: 0.6rem;
    letter-spacing: 0.12em; text-transform: uppercase;
    padding: 0.35rem 1rem; color: var(--muted); border-radius: 2px;
}
.nav-step.active { color: var(--gold); background: var(--gold-dim); border: 1px solid rgba(201,168,76,0.25); }
.nav-step.done { color: var(--green); }
.live-dot {
    display: flex; align-items: center; gap: 0.5rem;
    font-family: 'IBM Plex Mono', monospace; font-size: 0.58rem; letter-spacing: 0.1em; color: var(--green);
}
.live-dot::before {
    content: ''; width: 6px; height: 6px; background: var(--green);
    border-radius: 50%; box-shadow: 0 0 8px var(--green); animation: pulse 2s infinite;
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }

.page-wrapper { max-width: 1280px; margin: 0 auto; padding: 3rem 3rem 4rem; }

.hero { text-align: center; padding: 5rem 2rem 4rem; position: relative; }
.hero::before {
    content: ''; position: absolute; top: 0; left: 50%; transform: translateX(-50%);
    width: 600px; height: 1px;
    background: linear-gradient(90deg, transparent, var(--gold), transparent);
}
.hero-eyebrow {
    font-family: 'IBM Plex Mono', monospace; font-size: 0.65rem;
    letter-spacing: 0.3em; text-transform: uppercase; color: var(--gold); margin-bottom: 1.5rem;
}
.hero-title {
    font-family: 'Playfair Display', serif; font-size: 4rem; font-weight: 700;
    color: #fff; line-height: 1.1; margin-bottom: 1rem;
}
.hero-title span { color: var(--gold); }
.hero-subtitle {
    font-size: 1.1rem; color: var(--muted); max-width: 560px; margin: 0 auto 3rem; line-height: 1.7; font-weight: 300;
}

.section-label {
    font-family: 'IBM Plex Mono', monospace; font-size: 0.6rem;
    letter-spacing: 0.25em; text-transform: uppercase; color: var(--gold);
    margin-bottom: 1rem; display: flex; align-items: center; gap: 0.75rem;
}
.section-label::after { content: ''; flex: 1; height: 1px; background: linear-gradient(90deg, var(--border2), transparent); }
.section-title { font-family: 'Playfair Display', serif; font-size: 1.75rem; font-weight: 600; color: #fff; margin-bottom: 0.5rem; }
.section-divider { height: 1px; background: linear-gradient(90deg, var(--gold), transparent); width: 60px; margin-bottom: 2rem; }

.kpi-card {
    background: var(--surface); border: 1px solid var(--border);
    border-top: 2px solid var(--gold); border-radius: 4px; padding: 1.5rem 1.75rem;
}
.kpi-label {
    font-family: 'IBM Plex Mono', monospace; font-size: 0.58rem;
    letter-spacing: 0.18em; text-transform: uppercase; color: var(--muted); margin-bottom: 0.5rem;
}
.kpi-value { font-family: 'Playfair Display', serif; font-size: 2.2rem; font-weight: 600; color: #fff; line-height: 1; margin-bottom: 0.3rem; }
.kpi-sub { font-family: 'IBM Plex Mono', monospace; font-size: 0.62rem; color: var(--muted); }
.kpi-card.accent-green { border-top-color: var(--green); }
.kpi-card.accent-red { border-top-color: var(--red); }
.kpi-card.accent-amber { border-top-color: var(--amber); }

.price-card {
    background: var(--surface2); border: 1px solid var(--border);
    border-radius: 4px; padding: 1.25rem 1.5rem;
    display: flex; flex-direction: column; gap: 0.35rem;
}
.price-label { font-family: 'IBM Plex Mono', monospace; font-size: 0.55rem; letter-spacing: 0.18em; text-transform: uppercase; color: var(--muted); }
.price-value { font-family: 'Playfair Display', serif; font-size: 1.65rem; color: #fff; line-height: 1; }
.price-change { font-family: 'IBM Plex Mono', monospace; font-size: 0.62rem; }

.cta-hint { font-family: 'IBM Plex Mono', monospace; font-size: 0.6rem; letter-spacing: 0.12em; color: var(--muted); text-align: center; margin-top: 0.75rem; }

.stButton > button {
    background: linear-gradient(135deg, #c9a84c, #a8882a) !important;
    color: #09090e !important; border: none !important; border-radius: 3px !important;
    font-family: 'IBM Plex Mono', monospace !important; font-size: 0.7rem !important;
    font-weight: 600 !important; letter-spacing: 0.18em !important; text-transform: uppercase !important;
    padding: 0.75rem 2.5rem !important; transition: opacity 0.2s !important;
}
.stButton > button:hover { opacity: 0.85 !important; }

.verdict-card {
    background: var(--surface); border: 1px solid var(--border2); border-radius: 4px;
    padding: 2rem 2.5rem; display: flex; align-items: flex-start; gap: 2rem; margin: 1.5rem 0;
}
.verdict-title { font-family: 'Playfair Display', serif; font-size: 2rem; font-weight: 700; margin-bottom: 0.4rem; }
.verdict-body { font-size: 0.95rem; color: var(--muted); line-height: 1.6; max-width: 600px; }

.insight-row {
    display: flex; align-items: flex-start; gap: 1rem;
    padding: 1rem 1.25rem; margin: 0.4rem 0;
    background: var(--surface); border: 1px solid var(--border); border-radius: 3px;
    font-size: 0.9rem; line-height: 1.6; color: var(--text);
}
.signal-tag {
    font-family: 'IBM Plex Mono', monospace; font-size: 0.52rem;
    letter-spacing: 0.12em; text-transform: uppercase;
    padding: 0.18rem 0.5rem; border-radius: 2px; white-space: nowrap; margin-top: 0.18rem;
}
.tag-risk { background: rgba(242,101,90,0.12); color: var(--red); border: 1px solid rgba(242,101,90,0.3); }
.tag-watch { background: rgba(240,162,58,0.12); color: var(--amber); border: 1px solid rgba(240,162,58,0.3); }
.tag-stable { background: rgba(62,207,142,0.12); color: var(--green); border: 1px solid rgba(62,207,142,0.3); }

.action-row {
    display: flex; align-items: flex-start; gap: 1rem;
    padding: 1rem 1.25rem; margin: 0.4rem 0;
    background: rgba(201,168,76,0.04); border: 1px solid rgba(201,168,76,0.15);
    border-radius: 3px; font-size: 0.9rem; line-height: 1.6; color: var(--text);
}
.action-num { font-family: 'IBM Plex Mono', monospace; font-size: 0.6rem; color: var(--gold); min-width: 1.5rem; margin-top: 0.2rem; font-weight: 500; }

.stNumberInput input, .stTextInput input {
    background: var(--surface2) !important; border: 1px solid var(--border2) !important;
    border-radius: 3px !important; color: var(--text) !important;
    font-family: 'IBM Plex Mono', monospace !important; font-size: 0.85rem !important;
}
.stNumberInput input:focus, .stTextInput input:focus { border-color: var(--gold) !important; box-shadow: 0 0 0 2px rgba(201,168,76,0.1) !important; }
.stNumberInput label, .stTextInput label, .stSelectbox label {
    font-family: 'IBM Plex Mono', monospace !important; font-size: 0.6rem !important;
    letter-spacing: 0.15em !important; text-transform: uppercase !important; color: var(--muted) !important;
}
.stSelectbox > div > div { background: var(--surface2) !important; border: 1px solid var(--border2) !important; border-radius: 3px !important; color: var(--text) !important; }

.stTabs [data-baseweb="tab-list"] { background: var(--surface); border: 1px solid var(--border); border-radius: 3px; padding: 3px; gap: 2px; }
.stTabs [data-baseweb="tab"] { background: transparent !important; color: var(--muted) !important; border-radius: 2px !important; font-family: 'IBM Plex Mono', monospace !important; font-size: 0.65rem !important; letter-spacing: 0.08em !important; }
.stTabs [aria-selected="true"] { background: var(--gold-dim) !important; color: var(--gold) !important; border: 1px solid rgba(201,168,76,0.25) !important; }

.stDataFrame { border: 1px solid var(--border) !important; border-radius: 4px !important; }
hr { border-color: var(--border) !important; }

.gold-rule { height: 1px; background: linear-gradient(90deg, transparent, var(--gold), transparent); margin: 2.5rem 0; }
.ornament { text-align: center; font-family: 'IBM Plex Mono', monospace; font-size: 0.55rem; letter-spacing: 0.3em; color: var(--muted2); margin: 2rem 0; }
</style>
""", unsafe_allow_html=True)

# ── LOAD ─────────────────────────────────────────────────────────────────────
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
    try:
        t = yf.Ticker(ticker)
        fi = getattr(t, "fast_info", None)
        if fi is not None:
            last = getattr(fi, "last_price", None)
            if last is None:
                try: last = fi.get("last_price")
                except: last = None
            if last is not None and not pd.isna(last) and float(last) != 0:
                return round(float(last), 2)
        for period in ("5d", "1mo", "3mo"):
            df = t.history(period=period, interval="1d", auto_adjust=False, prepost=True, actions=False)
            if df is not None and not df.empty and "Close" in df.columns:
                s = df["Close"].dropna()
                if not s.empty:
                    return round(float(s.iloc[-1]), 2)
        df2 = yf.download(ticker, period="5d", interval="1d", progress=False)
        if df2 is not None and not df2.empty and "Close" in df2.columns:
            s2 = df2["Close"].dropna()
            if not s2.empty:
                return round(float(s2.iloc[-1]), 2)
    except: pass
    return None

model, features, targets = load_model()
df_hist = load_history()
historical_means = df_hist[features].mean().to_dict()

if model is None:
    st.error("Model not found — please run ml_model.py first.")
    st.stop()

plot_theme = dict(
    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    font=dict(family="IBM Plex Mono", color="#5a5d7a", size=11),
    xaxis=dict(gridcolor="#1e2030", color="#5a5d7a", linecolor="#1e2030"),
    yaxis=dict(gridcolor="#1e2030", color="#5a5d7a", linecolor="#1e2030"),
    margin=dict(t=40, b=20, l=10, r=10),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#5a5d7a", size=10))
)

# ── SESSION STATE ─────────────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "welcome"
if "prediction_result" not in st.session_state:
    st.session_state.prediction_result = None

def go_to(page):
    st.session_state.page = page
    st.rerun()

# ── NAVBAR ────────────────────────────────────────────────────────────────────
steps = [("welcome", "01  Overview"), ("simulate", "02  Simulation"), ("recommend", "03  Recommendations")]
current = st.session_state.page

step_html = ""
for key, label in steps:
    idx_cur = [k for k, _ in steps].index(current)
    idx_key = [k for k, _ in steps].index(key)
    cls = "active" if key == current else ("done" if idx_key < idx_cur else "")
    step_html += f"<div class='nav-step {cls}'>{label}</div>"

st.markdown(f"""
<div class='navbar'>
    <div>
        <div class='nav-brand'>Biz<span>Shock</span></div>
        <div class='nav-tagline'>Commodity Shock &middot; Business Impact Analyzer</div>
    </div>
    <div class='nav-steps'>{step_html}</div>
    <div class='live-dot'>Live Market Data</div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — WELCOME
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "welcome":
    st.markdown("<div class='page-wrapper'>", unsafe_allow_html=True)

    st.markdown("""
    <div class='hero'>
        <div class='hero-eyebrow'>Economic Intelligence Platform</div>
        <div class='hero-title'>Welcome to <span>BizShock</span></div>
        <div class='hero-subtitle'>
            Understand how global commodity price shocks impact your business.
            Powered by machine learning and live market data.
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_l, col_c, col_r = st.columns([2, 1, 2])
    with col_c:
        if st.button("Begin Simulation  ▶"):
            go_to("simulate")
    st.markdown("<div class='cta-hint'>Configure your business profile and run a scenario prediction</div>", unsafe_allow_html=True)

    st.markdown("<div class='gold-rule'></div>", unsafe_allow_html=True)

    # Live prices
    st.markdown("""
    <div class='section-label'>Live Market Snapshot</div>
    <div class='section-title'>Current Commodity Prices</div>
    <div class='section-divider'></div>
    """, unsafe_allow_html=True)

    key_tickers = {
        "Crude Oil": ("CL=F", "CRUDE_OIL"),
        "Natural Gas": ("NG=F", "NATURAL_GAS"),
        "Wheat": ("ZW=F", "WHEAT"),
        "Copper": ("HG=F", "COPPER"),
        "Coffee": ("KC=F", "COFFEE"),
        "Cotton": ("CT=F", "COTTON"),
    }
    pcols = st.columns(6)
    for i, (name, (ticker, hist_key)) in enumerate(key_tickers.items()):
        price = fetch_live_price(ticker)
        hist = historical_means.get(hist_key, 0)
        if price and hist:
            chg = (price - hist) / hist * 100
            arrow = "▲" if chg > 0 else "▼"
            chg_color = "#f2655a" if chg > 5 else "#f0a23a" if chg > 0 else "#3ecf8e"
            chg_str = f"{arrow} {abs(chg):.1f}%  vs  avg"
        else:
            chg_color, chg_str = "#5a5d7a", "N / A"
        price_str = f"${price:,.2f}" if price else "—"
        pcols[i].markdown(f"""
        <div class='price-card'>
            <div class='price-label'>{name}</div>
            <div class='price-value'>{price_str}</div>
            <div class='price-change' style='color:{chg_color}'>{chg_str}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div class='gold-rule'></div>", unsafe_allow_html=True)

    # Historical KPIs
    st.markdown("""
    <div class='section-label'>Historical Context</div>
    <div class='section-title'>Key Economic Indicators</div>
    <div class='section-divider'></div>
    """, unsafe_allow_html=True)

    k1, k2, k3, k4 = st.columns(4)
    kpis = [
        ("Average Inflation", f"{df_hist['Inflation (CPI %)'].mean():.2f}%",
         f"Historical Peak:  {df_hist['Inflation (CPI %)'].max():.2f}%", "accent-red"),
        ("Average GDP Growth", f"{df_hist['GDP Growth (% Annual)'].mean():.2f}%",
         f"Latest Reading:  {df_hist['GDP Growth (% Annual)'].iloc[-1]:.2f}%", "accent-green"),
        ("Average Unemployment", f"{df_hist['Unemployment Rate (%)'].mean():.2f}%",
         f"Historical Low:  {df_hist['Unemployment Rate (%)'].min():.2f}%", "accent-amber"),
        ("Average Interest Rate", f"{df_hist['Interest Rate (Real, %)'].mean():.2f}%",
         f"Latest Reading:  {df_hist['Interest Rate (Real, %)'].iloc[-1]:.2f}%", ""),
    ]
    for col, (label, value, sub, cls) in zip([k1, k2, k3, k4], kpis):
        col.markdown(f"""
        <div class='kpi-card {cls}'>
            <div class='kpi-label'>{label}</div>
            <div class='kpi-value'>{value}</div>
            <div class='kpi-sub'>{sub}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Historical charts
    st.markdown("""
    <div class='section-label'>Macro Trend Explorer</div>
    <div class='section-title'>Historical Indicator Charts</div>
    <div class='section-divider'></div>
    """, unsafe_allow_html=True)

    tab_labels = [t.split("(")[0].strip() for t in targets]
    tabs = st.tabs(tab_labels)
    for tab, target in zip(tabs, targets):
        with tab:
            series = df_hist[target]
            avg = float(series.mean())
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_hist.index, y=series, mode="lines",
                line=dict(color="#c9a84c", width=1.5), name=target,
                fill="tozeroy", fillcolor="rgba(201,168,76,0.06)"
            ))
            fig.add_trace(go.Scatter(
                x=df_hist.index, y=series, mode="markers",
                marker=dict(size=4, color="#c9a84c", line=dict(color="#09090e", width=1)),
                showlegend=False
            ))
            fig.add_hline(y=avg, line_dash="dot", line_color="#2a2d44", line_width=1,
                          annotation_text=f"  Mean:  {avg:.2f}%",
                          annotation_font=dict(color="#5a5d7a", size=10, family="IBM Plex Mono"))
            last_x, last_y = series.index[-1], float(series.iloc[-1])
            fig.add_trace(go.Scatter(
                x=[last_x], y=[last_y], mode="markers",
                marker=dict(size=9, color="#c9a84c", line=dict(color="#fff", width=1.5)),
                showlegend=False
            ))
            fig.update_layout(**plot_theme, height=300)
            st.plotly_chart(fig, use_container_width=True)

            sc1, sc2, sc3, sc4 = st.columns(4)
            stats = [
                ("Mean", f"{series.mean():.2f}%", ""),
                ("Peak", f"{series.max():.2f}%", "accent-red"),
                ("Trough", f"{series.min():.2f}%", "accent-green"),
                ("Latest", f"{series.iloc[-1]:.2f}%", ""),
            ]
            for scol, (slabel, sval, scls) in zip([sc1, sc2, sc3, sc4], stats):
                scol.markdown(f"""
                <div class='kpi-card {scls}' style='padding:1rem 1.25rem'>
                    <div class='kpi-label'>{slabel}</div>
                    <div class='kpi-value' style='font-size:1.5rem'>{sval}</div>
                </div>""", unsafe_allow_html=True)

    st.markdown("<div class='gold-rule'></div>", unsafe_allow_html=True)
    st.markdown("<div class='ornament'>── ◆ ──</div>", unsafe_allow_html=True)

    col_l2, col_c2, col_r2 = st.columns([2, 1, 2])
    with col_c2:
        if st.button("Predict Your Simulation  ▶"):
            go_to("simulate")
    st.markdown("<div class='cta-hint'>Proceed to configure your business and run a custom scenario</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — SIMULATION
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "simulate":
    st.markdown("<div class='page-wrapper'>", unsafe_allow_html=True)

    col_back, _ = st.columns([1, 5])
    with col_back:
        if st.button("← Back to Overview"):
            go_to("welcome")

    st.markdown("""
    <div class='section-label'>Business Simulation</div>
    <div class='section-title'>Configure Your Scenario</div>
    <div class='section-divider'></div>
    """, unsafe_allow_html=True)

    cfg1, cfg2 = st.columns([2, 1])
    with cfg1:
        business_type = st.selectbox("Business Type", get_all_profiles(), index=0)
    with cfg2:
        scenario_name = st.text_input("Scenario Label", value="scenario_01")

    profile = BUSINESS_PROFILES[business_type]
    st.markdown(f"""
    <div style='font-family:IBM Plex Mono,monospace;font-size:0.62rem;color:#5a5d7a;
    margin-top:-0.5rem;margin-bottom:1.5rem;letter-spacing:0.06em'>
    Profile description:  {profile["description"]}
    </div>""", unsafe_allow_html=True)

    st.markdown("<div class='gold-rule'></div>", unsafe_allow_html=True)

    st.markdown("""
    <div class='section-label'>Cost Basket</div>
    <div class='section-title'>Commodity Exposure Weights</div>
    <div class='section-divider'></div>
    """, unsafe_allow_html=True)

    if business_type == "🛠 Custom":
        if "custom_commodities" not in st.session_state:
            st.session_state.custom_commodities = [{"name": "Crude Oil", "weight": 50}]
        for i, row in enumerate(st.session_state.custom_commodities):
            cc1, cc2, cc3 = st.columns([3, 2, 1])
            with cc1:
                name = st.selectbox("Commodity", list(ALL_COMMODITIES.keys()), key=f"name_{i}",
                                    index=list(ALL_COMMODITIES.keys()).index(row["name"]) if row["name"] in ALL_COMMODITIES else 0)
                st.session_state.custom_commodities[i]["name"] = name
            with cc2:
                weight = st.number_input("Weight (%)", 0, 100, row["weight"], key=f"weight_{i}")
                st.session_state.custom_commodities[i]["weight"] = weight
            with cc3:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Remove", key=f"remove_{i}") and len(st.session_state.custom_commodities) > 1:
                    st.session_state.custom_commodities.pop(i)
                    st.rerun()
        if st.button("+ Add Commodity"):
            st.session_state.custom_commodities.append({"name": "Wheat", "weight": 10})
            st.rerun()
        total_weight = sum(r["weight"] for r in st.session_state.custom_commodities)
        color = "#3ecf8e" if total_weight == 100 else "#f2655a"
        st.markdown(f"<div style='font-family:IBM Plex Mono,monospace;font-size:0.7rem;color:{color};margin-top:0.5rem'>Total weight:  {total_weight}%  {'✓  Correct' if total_weight==100 else '—  Must equal 100%'}</div>", unsafe_allow_html=True)
        active_commodities = {}
        for row in st.session_state.custom_commodities:
            com = ALL_COMMODITIES.get(row["name"])
            if com:
                key = row["name"].upper().replace(" ", "_")
                active_commodities[key] = {"ticker": com["ticker"], "weight": row["weight"] / 100}
    else:
        active_commodities = dict(profile["commodities"])
        wcols = st.columns(len(active_commodities))
        for i, (commodity, info) in enumerate(active_commodities.items()):
            with wcols[i]:
                new_weight = st.number_input(
                    commodity.replace("_", " ").title(),
                    0, 100, int(info["weight"] * 100), key=f"w_{commodity}"
                )
                active_commodities[commodity]["weight"] = new_weight / 100

    st.markdown("<div class='gold-rule'></div>", unsafe_allow_html=True)

    st.markdown("""
    <div class='section-label'>Live Market Data</div>
    <div class='section-title'>Current Input Commodity Prices</div>
    <div class='section-divider'></div>
    """, unsafe_allow_html=True)

    live_prices = {}
    lp_cols = st.columns(len(active_commodities))
    for i, (commodity, info) in enumerate(active_commodities.items()):
        price = fetch_live_price(info["ticker"])
        live_prices[commodity] = price
        hist = historical_means.get(commodity, 0)
        if price is None:
            price_str, chg_str, chg_color = "N / A", "No live data available", "#5a5d7a"
        else:
            price_str = f"${price:,.2f}"
            if hist:
                chg = (price - hist) / hist * 100
                arrow = "▲" if chg > 0 else "▼"
                chg_color = "#f2655a" if chg > 5 else "#f0a23a" if chg > 0 else "#3ecf8e"
                chg_str = f"{arrow}  {abs(chg):.1f}%  vs  historical avg"
            else:
                chg_str, chg_color = "Baseline unavailable", "#5a5d7a"
        with lp_cols[i]:
            st.markdown(f"""
            <div class='price-card'>
                <div class='price-label'>{commodity.replace("_", " ").title()}</div>
                <div class='price-value'>{price_str}</div>
                <div class='price-change' style='color:{chg_color}'>{chg_str}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    col_l, col_c, col_r = st.columns([2, 1, 2])
    with col_c:
        run_btn = st.button("Run Prediction  ▶")

    if run_btn:
        input_data = {f: (live_prices.get(f) if live_prices.get(f) is not None else historical_means.get(f, 0)) for f in features}
        input_df = pd.DataFrame([input_data])[features]
        prediction = model.predict(input_df)[0]
        result = dict(zip(targets, prediction))

        baseline_df = pd.DataFrame([{f: historical_means.get(f, 0) for f in features}])
        baseline = dict(zip(targets, model.predict(baseline_df)[0]))

        cost_impact, breakdown = calculate_cost_impact(active_commodities, live_prices, historical_means)
        translation = translate(result, business_type, cost_impact)

        st.session_state.prediction_result = {
            "result": result, "baseline": baseline,
            "cost_impact": cost_impact, "breakdown": breakdown,
            "translation": translation, "business_type": business_type,
            "scenario_name": scenario_name, "live_prices": live_prices,
            "active_commodities": active_commodities,
        }

        os.makedirs(RESULTS_DIR, exist_ok=True)
        out = {
            "business": business_type, "scenario": scenario_name,
            "live_prices": live_prices, "predictions": result,
            "baseline": baseline, "cost_impact_pct": cost_impact,
            "verdict": translation["verdict"][0]
        }
        json.dump(out, open(os.path.join(RESULTS_DIR, f"{scenario_name}_prediction.json"), "w"), indent=2)
        go_to("recommend")

    st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — RECOMMENDATIONS
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "recommend":
    if st.session_state.prediction_result is None:
        st.warning("No prediction found. Please run a simulation first.")
        col_l, col_c, col_r = st.columns([2, 1, 2])
        with col_c:
            if st.button("Go to Simulation  ▶"):
                go_to("simulate")
        st.stop()

    pr            = st.session_state.prediction_result
    result        = pr["result"]
    baseline      = pr["baseline"]
    cost_impact   = pr["cost_impact"]
    breakdown     = pr["breakdown"]
    translation   = pr["translation"]
    business_type = pr["business_type"]
    scenario_name = pr["scenario_name"]
    live_prices   = pr["live_prices"]
    active_commodities = pr["active_commodities"]
    verdict_text, verdict_desc, verdict_color = translation["verdict"]

    st.markdown("<div class='page-wrapper'>", unsafe_allow_html=True)

    col_back, _ = st.columns([1, 5])
    with col_back:
        if st.button("← Back to Simulation"):
            go_to("simulate")

    st.markdown(f"""
    <div class='section-label'>Analysis Complete &nbsp;&middot;&nbsp; {business_type} &nbsp;&middot;&nbsp; {scenario_name}</div>
    <div class='section-title'>Strategic Recommendations</div>
    <div class='section-divider'></div>
    """, unsafe_allow_html=True)

    # Verdict
    verdict_icon = "🔴" if "Tough" in verdict_text else "🟡" if "Caution" in verdict_text else "🟢"
    st.markdown(f"""
    <div class='verdict-card'>
        <div style='font-size:2.5rem;line-height:1'>{verdict_icon}</div>
        <div>
            <div class='verdict-title' style='color:{verdict_color}'>{verdict_text}</div>
            <div class='verdict-body'>{verdict_desc}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='gold-rule'></div>", unsafe_allow_html=True)

    # Predicted KPIs
    st.markdown("""
    <div class='section-label'>Predicted Outcomes</div>
    <div class='section-title'>Macro Indicator Forecast</div>
    <div class='section-divider'></div>
    """, unsafe_allow_html=True)

    res_cols = st.columns(len(targets))
    for i, (target, value) in enumerate(result.items()):
        diff = value - baseline[target]
        arrow = "▲" if diff > 0 else "▼"
        is_bad = (diff > 0 and target != "GDP Growth (% Annual)") or (diff < 0 and target == "GDP Growth (% Annual)")
        diff_color = "#f2655a" if is_bad else "#3ecf8e"
        cls = "accent-red" if is_bad else "accent-green"
        with res_cols[i]:
            st.markdown(f"""
            <div class='kpi-card {cls}'>
                <div class='kpi-label'>{target.split("(")[0].strip()}</div>
                <div class='kpi-value'>{value:.1f}%</div>
                <div class='kpi-sub' style='color:{diff_color}'>{arrow}  {abs(diff):.2f} pp  vs  baseline</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Chart + breakdown
    ch_left, ch_right = st.columns(2)
    with ch_left:
        st.markdown("""
        <div class='section-label'>Visual Comparison</div>
        <div class='section-title' style='font-size:1.2rem'>Scenario vs Baseline</div>
        <div class='section-divider'></div>
        """, unsafe_allow_html=True)
        short = [t.split("(")[0].strip() for t in targets]
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name="Baseline", x=short, y=[baseline[t] for t in targets],
            marker_color="#1e2030", marker_line_color="#2a2d44", marker_line_width=1
        ))
        fig.add_trace(go.Bar(
            name="Scenario", x=short, y=[result[t] for t in targets],
            marker_color="#c9a84c", marker_line_color="#c9a84c", marker_line_width=0
        ))
        fig.update_layout(**plot_theme, barmode="group", height=280)
        st.plotly_chart(fig, use_container_width=True)

    with ch_right:
        st.markdown("""
        <div class='section-label'>Cost Analysis</div>
        <div class='section-title' style='font-size:1.2rem'>Input Cost Impact</div>
        <div class='section-divider'></div>
        """, unsafe_allow_html=True)
        if breakdown:
            bd_df = pd.DataFrame(breakdown).T.reset_index()
            bd_df.columns = ["Commodity", "Live Price", "Hist. Avg", "Change %", "Weight", "Impact %"]
            st.dataframe(
                bd_df.style.format({
                    "Live Price": "{:.2f}", "Hist. Avg": "{:.2f}",
                    "Change %": "{:+.1f}", "Weight": "{:.0%}", "Impact %": "{:+.2f}"
                }),
                use_container_width=True, hide_index=True
            )
            imp_color = "#f2655a" if cost_impact > 10 else "#f0a23a" if cost_impact > 0 else "#3ecf8e"
            st.markdown(f"""
            <div style='font-family:IBM Plex Mono,monospace;font-size:0.72rem;
            color:{imp_color};margin-top:0.75rem;letter-spacing:0.06em'>
            Total Input Cost Impact:  {cost_impact:+.1f}%
            </div>""", unsafe_allow_html=True)

    st.markdown("<div class='gold-rule'></div>", unsafe_allow_html=True)

    # Insights + Actions
    col_ins, col_act = st.columns(2)
    with col_ins:
        st.markdown("""
        <div class='section-label'>Market Signals</div>
        <div class='section-title' style='font-size:1.2rem'>Key Risk Indicators</div>
        <div class='section-divider'></div>
        """, unsafe_allow_html=True)
        for insight in translation["insights"]:
            tag = "RISK" if "🔴" in insight else "WATCH" if "🟡" in insight else "STABLE"
            tag_cls = "tag-risk" if "🔴" in insight else "tag-watch" if "🟡" in insight else "tag-stable"
            text = insight[2:].strip().replace("**", "")
            st.markdown(f"""
            <div class='insight-row'>
                <span class='signal-tag {tag_cls}'>{tag}</span>
                {text}
            </div>""", unsafe_allow_html=True)

    with col_act:
        st.markdown("""
        <div class='section-label'>Action Plan</div>
        <div class='section-title' style='font-size:1.2rem'>Recommended Actions</div>
        <div class='section-divider'></div>
        """, unsafe_allow_html=True)
        for i, action in enumerate(translation["actions"], 1):
            text = action[2:].strip()
            st.markdown(f"""
            <div class='action-row'>
                <span class='action-num'>{i:02d}</span>
                {text}
            </div>""", unsafe_allow_html=True)

    st.markdown("<div class='gold-rule'></div>", unsafe_allow_html=True)

    # Scenario history
    st.markdown("""
    <div class='section-label'>Scenario History</div>
    <div class='section-title'>Previous Simulations</div>
    <div class='section-divider'></div>
    """, unsafe_allow_html=True)
    files = [f for f in os.listdir(RESULTS_DIR) if f.endswith("_prediction.json")] if os.path.exists(RESULTS_DIR) else []
    if files:
        rows = []
        for f in files:
            data = json.load(open(os.path.join(RESULTS_DIR, f)))
            row = {
                "Scenario": data.get("scenario", ""), "Business": data.get("business", ""),
                "Verdict": data.get("verdict", ""), "Cost Δ %": data.get("cost_impact_pct", 0)
            }
            row.update(data.get("predictions", {}))
            rows.append(row)
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.markdown("<div style='font-family:IBM Plex Mono,monospace;font-size:0.7rem;color:#3a3d55;padding:1.25rem 0'>No prior simulations saved.</div>", unsafe_allow_html=True)

    st.markdown("<div class='gold-rule'></div>", unsafe_allow_html=True)
    st.markdown("<div class='ornament'>── ◆ ──</div>", unsafe_allow_html=True)

    col_l, col_c, col_r = st.columns([2, 1, 2])
    with col_c:
        if st.button("Run Another Simulation  ▶"):
            st.session_state.prediction_result = None
            go_to("simulate")
    st.markdown("<div class='cta-hint'>Return to configure a new business scenario</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
