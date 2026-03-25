# takes macro predictions and translates them into plain business language
# so a small business owner actually understands what to do

def translate(predictions, business_type, cost_impact_pct):

    inflation    = predictions.get("Inflation (CPI %)", 4.0)
    gdp_growth   = predictions.get("GDP Growth (% Annual)", 3.5)
    unemployment = predictions.get("Unemployment Rate (%)", 7.0)
    interest     = predictions.get("Interest Rate (Real, %)", 2.0)

    insights = []
    actions  = []

    # ── cost impact ───────────────────────────────────────────────────────────
    if cost_impact_pct > 20:
        insights.append(f"🔴 Your input costs are estimated to rise by **{cost_impact_pct:.1f}%** — this is severe")
        actions.append("💡 Renegotiate supplier contracts immediately or find alternative suppliers")
    elif cost_impact_pct > 10:
        insights.append(f"🟡 Your input costs may rise by **{cost_impact_pct:.1f}%** — manageable but watch closely")
        actions.append("💡 Start reducing wastage and tighten inventory to offset rising costs")
    else:
        insights.append(f"🟢 Your input costs are relatively stable — estimated rise of **{cost_impact_pct:.1f}%**")

    # ── inflation ─────────────────────────────────────────────────────────────
    if inflation > 7:
        insights.append(f"🔴 Inflation is high at **{inflation:.1f}%** — everything gets more expensive")
        actions.append("💡 Consider raising your prices gradually — customers expect it during high inflation")
    elif inflation > 5:
        insights.append(f"🟡 Inflation at **{inflation:.1f}%** — moderate pressure on your costs and customers")
        actions.append("💡 Hold prices for now but review every 3 months")
    else:
        insights.append(f"🟢 Inflation is under control at **{inflation:.1f}%** — good environment for business")

    # ── gdp growth ────────────────────────────────────────────────────────────
    if gdp_growth < 1:
        insights.append(f"🔴 GDP growth is very low at **{gdp_growth:.1f}%** — economy is nearly stagnant")
        actions.append("💡 Focus on retaining existing customers rather than acquiring new ones")
        actions.append("💡 Delay any major expansion plans until growth recovers")
    elif gdp_growth < 2.5:
        insights.append(f"🟡 GDP growth is slow at **{gdp_growth:.1f}%** — consumers will be cautious with spending")
        actions.append("💡 Introduce budget-friendly offerings to retain price-sensitive customers")
    else:
        insights.append(f"🟢 GDP growth is healthy at **{gdp_growth:.1f}%** — consumer spending should remain strong")

    # ── unemployment ──────────────────────────────────────────────────────────
    if unemployment > 9:
        insights.append(f"🔴 Unemployment is high at **{unemployment:.1f}%** — people have less money to spend")
        actions.append("💡 Offer value deals or loyalty programs to keep customers coming back")
    elif unemployment > 7.5:
        insights.append(f"🟡 Unemployment at **{unemployment:.1f}%** — some softness in consumer demand expected")
    else:
        insights.append(f"🟢 Unemployment is low at **{unemployment:.1f}%** — good for consumer spending")

    # ── interest rate ─────────────────────────────────────────────────────────
    if interest > 5:
        insights.append(f"🔴 Interest rates are high at **{interest:.1f}%** — borrowing is very expensive")
        actions.append("💡 Avoid taking new loans right now — wait for rates to come down")
        actions.append("💡 If you have existing variable rate loans, try to refinance or pay down faster")
    elif interest > 3:
        insights.append(f"🟡 Interest rates at **{interest:.1f}%** — borrowing is moderately expensive")
        actions.append("💡 Only borrow if absolutely necessary — keep debt minimal")
    else:
        insights.append(f"🟢 Interest rates are low at **{interest:.1f}%** — good time to invest or expand if needed")

    # ── business specific advice ──────────────────────────────────────────────
    business_advice = get_business_advice(business_type, inflation, gdp_growth, interest)
    if business_advice:
        actions.extend(business_advice)

    # ── overall verdict ───────────────────────────────────────────────────────
    red_count = sum(1 for i in insights if "🔴" in i)
    if red_count >= 3:
        verdict = ("🔴 Tough Times Ahead", "The macro environment looks difficult for your business right now. Focus on cutting costs and holding cash.", "#ef4444")
    elif red_count >= 1:
        verdict = ("🟡 Proceed with Caution", "Mixed signals — some risks ahead but manageable with the right moves.", "#f59e0b")
    else:
        verdict = ("🟢 Favorable conditions", "The macro environment looks supportive for your business. Good time to grow.", "#22c55e")

    return {"insights": insights, "actions": actions, "verdict": verdict}


def get_business_advice(business_type, inflation, gdp_growth, interest):
    advice = []

    if "Bakery" in business_type:
        if inflation > 5:
            advice.append("💡 Wheat and sugar prices are volatile — buy in bulk now to lock in lower prices")
        if gdp_growth < 2:
            advice.append("💡 Offer smaller portion sizes at lower price points to keep footfall up")

    elif "Textile" in business_type:
        if inflation > 5:
            advice.append("💡 Cotton prices are likely rising — consider synthetic alternatives temporarily")
        if interest > 4:
            advice.append("💡 Delay machinery upgrades — high interest makes financing expensive")

    elif "Restaurant" in business_type:
        if inflation > 6:
            advice.append("💡 Simplify your menu to fewer ingredients — reduces waste and cost")
        if gdp_growth < 2:
            advice.append("💡 Lunch deals and combo offers work better during slow growth periods")

    elif "Farm" in business_type:
        if inflation > 5:
            advice.append("💡 Good time to sell stored produce — prices are high")
        if gdp_growth < 2:
            advice.append("💡 Shift to staple crops — demand stays stable even in downturns")

    elif "Transport" in business_type:
        if inflation > 5:
            advice.append("💡 Fuel costs are your biggest risk — explore fuel hedging or route optimization")

    elif "Construction" in business_type:
        if interest > 4:
            advice.append("💡 Real estate slowdown likely — focus on government contracts which are more stable")

    elif "Cafe" in business_type:
        if inflation > 5:
            advice.append("💡 Coffee prices are rising — lock in supplier contracts for next 6 months")

    return advice


def calculate_cost_impact(profile_commodities, live_prices, historical_means):
    """
    calculates weighted average cost impact % for the business
    based on how much commodity prices have moved vs historical average
    """
    total_impact = 0.0
    breakdown = {}

    for commodity, info in profile_commodities.items():
        weight = info["weight"]
        live = live_prices.get(commodity)
        hist = historical_means.get(commodity)

        if live and hist and hist > 0:
            pct_change = ((live - hist) / hist) * 100
            weighted_impact = pct_change * weight
            total_impact += weighted_impact
            breakdown[commodity] = {
                "live_price": live,
                "historical_avg": round(hist, 2),
                "change_pct": round(pct_change, 2),
                "weight": weight,
                "weighted_impact": round(weighted_impact, 2)
            }

    return round(total_impact, 2), breakdown
```

---

Now we have all 3 pieces ready:
```
✅ business_profiles.py   — what commodities each business uses
✅ business_translator.py — macro numbers → business language
✅ now we rewrite app.py  — the full dashboard