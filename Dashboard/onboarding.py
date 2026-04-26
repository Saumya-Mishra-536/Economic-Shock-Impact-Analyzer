"""
Onboarding tooltips and plain-English help text for BizShock.
"""

TOOLTIPS = {
    "commodity_weight": """
    <div style='font-family:IBM Plex Mono,monospace;font-size:0.75rem;
    background:#0f1018;border:1px solid #2a2d44;border-left:3px solid #c9a84c;
    border-radius:3px;padding:1rem 1.25rem;margin-bottom:1rem;line-height:1.7;color:#e2e4f0'>
    <div style='color:#c9a84c;font-size:0.6rem;letter-spacing:0.18em;text-transform:uppercase;margin-bottom:0.5rem'>
    What is a Commodity Weight?</div>
    A <strong>weight</strong> represents how much a commodity contributes to your total costs.
    For example, if 40% of your bakery's cost is flour (wheat), set Wheat to 40.
    All weights must add up to 100%.
    </div>""",

    "scenario_label": """
    <div style='font-family:IBM Plex Mono,monospace;font-size:0.75rem;
    background:#0f1018;border:1px solid #2a2d44;border-left:3px solid #c9a84c;
    border-radius:3px;padding:0.75rem 1.25rem;margin-bottom:1rem;line-height:1.7;color:#e2e4f0'>
    <div style='color:#c9a84c;font-size:0.6rem;letter-spacing:0.18em;text-transform:uppercase;margin-bottom:0.5rem'>
    What is a Scenario Label?</div>
    A name you give this prediction run — e.g. <strong>oil_spike_jan</strong> or
    <strong>wheat_crisis_test</strong>. Used to save and compare simulations later.
    </div>""",

    "r2_score": """
    <div style='font-family:IBM Plex Mono,monospace;font-size:0.75rem;
    background:#0f1018;border:1px solid #2a2d44;border-left:3px solid #c9a84c;
    border-radius:3px;padding:0.75rem 1.25rem;margin-bottom:1rem;line-height:1.7;color:#e2e4f0'>
    <div style='color:#c9a84c;font-size:0.6rem;letter-spacing:0.18em;text-transform:uppercase;margin-bottom:0.5rem'>
    What is R² Score?</div>
    R² measures how well the model explains real-world data.
    <strong>1.0 = perfect</strong>, <strong>0.0 = no better than guessing the average</strong>.
    Above 0.85 is considered excellent for macroeconomic models.
    </div>""",
}

MAE_VALUES = {
    "Inflation (CPI %)":       1.389,
    "GDP Growth (% Annual)":   0.696,
    "Unemployment Rate (%)":   0.466,
    "Interest Rate (Real, %)": 0.990,
}

HISTORICAL_SCENARIOS = {
    "2008 Financial Crisis": {
        "description": "Global banking collapse — oil spike then crash, credit freeze",
        "year": 2008,
        "overrides": {"CRUDE_OIL": 99.67, "NATURAL_GAS": 8.86, "COPPER": 3.15},
    },
    "2020 COVID Shock": {
        "description": "Pandemic — demand collapse, supply chain disruption",
        "year": 2020,
        "overrides": {"CRUDE_OIL": 41.47, "NATURAL_GAS": 2.03, "WHEAT": 5.11},
    },
    "2022 Energy Crisis": {
        "description": "Ukraine war — energy and food price surge",
        "year": 2022,
        "overrides": {"CRUDE_OIL": 94.53, "NATURAL_GAS": 6.45, "WHEAT": 9.12, "CORN": 6.82},
    },
    "2011 Arab Spring": {
        "description": "Geopolitical instability — food and oil spike",
        "year": 2011,
        "overrides": {"CRUDE_OIL": 111.0, "WHEAT": 8.00, "CORN": 7.00, "SUGAR": 26.0},
    },
}

def render_first_visit_banner():
    return """
    <div style='
        background: linear-gradient(135deg, rgba(201,168,76,0.08), rgba(201,168,76,0.03));
        border: 1px solid rgba(201,168,76,0.3);
        border-radius: 4px;
        padding: 1.5rem 2rem;
        margin-bottom: 2rem;
    '>
        <div style='font-family:IBM Plex Mono,monospace;font-size:0.6rem;
        letter-spacing:0.2em;text-transform:uppercase;color:#c9a84c;margin-bottom:0.75rem'>
        Getting Started
        </div>
        <div style='font-family:Source Sans 3,sans-serif;font-size:1rem;
        color:#e2e4f0;line-height:1.7;margin-bottom:0.75rem'>
        <strong>BizShock</strong> predicts how global commodity price shocks affect your business
        using a machine learning model trained on 50 years of economic data.
        </div>
        <div style='font-family:IBM Plex Mono,monospace;font-size:0.72rem;
        color:#5a5d7a;line-height:1.9'>
        <span style='color:#c9a84c'>01</span> &nbsp; Select your business type below<br>
        <span style='color:#c9a84c'>02</span> &nbsp; Review your commodity cost weights<br>
        <span style='color:#c9a84c'>03</span> &nbsp; Hit <strong style='color:#e2e4f0'>Run Prediction</strong> — results appear in under 3 seconds<br>
        <span style='color:#c9a84c'>04</span> &nbsp; Download your PDF report or compare scenarios
        </div>
    </div>
    """

def render_confidence_note(result, mae_values):
    rows = ""
    for target, value in result.items():
        mae = mae_values.get(target, 0)
        low  = value - mae
        high = value + mae
        rows += f"""
        <div style='display:flex;justify-content:space-between;
        padding:0.5rem 0;border-bottom:1px solid #1e2030;
        font-family:IBM Plex Mono,monospace;font-size:0.7rem'>
            <span style='color:#5a5d7a'>{target.split("(")[0].strip()}</span>
            <span style='color:#e2e4f0'>{value:.1f}%
                <span style='color:#3a3d55;font-size:0.62rem'>
                &nbsp; ({low:.1f}% – {high:.1f}%)
                </span>
            </span>
        </div>"""
    return f"""
    <div style='background:#0f1018;border:1px solid #2a2d44;border-radius:4px;
    padding:1.25rem 1.5rem;margin-top:1rem'>
        <div style='font-family:IBM Plex Mono,monospace;font-size:0.6rem;
        letter-spacing:0.18em;text-transform:uppercase;color:#c9a84c;margin-bottom:0.75rem'>
        Prediction Ranges (95% confidence based on model MAE)
        </div>
        {rows}
        <div style='font-family:IBM Plex Mono,monospace;font-size:0.58rem;
        color:#3a3d55;margin-top:0.75rem'>
        Ranges derived from model Mean Absolute Error validated on held-out data.
        </div>
    </div>"""
