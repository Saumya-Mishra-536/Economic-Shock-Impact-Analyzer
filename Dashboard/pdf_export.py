"""
BizShock PDF Report Generator
Generates a branded PDF report from a prediction result dict.
"""
import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

# ── Colour palette ─────────────────────────────────────────────────────────────
GOLD     = colors.HexColor("#c9a84c")
DARK     = colors.HexColor("#09090e")
SURFACE  = colors.HexColor("#0f1018")
SURFACE2 = colors.HexColor("#14151f")
BORDER   = colors.HexColor("#2a2d44")
TEXT     = colors.HexColor("#e2e4f0")
MUTED    = colors.HexColor("#5a5d7a")
GREEN    = colors.HexColor("#3ecf8e")
RED      = colors.HexColor("#f2655a")
AMBER    = colors.HexColor("#f0a23a")
WHITE    = colors.white

W, H = A4  # 595 x 842 pt

# ── Styles ─────────────────────────────────────────────────────────────────────
def styles():
    return {
        "title": ParagraphStyle("title",
            fontName="Helvetica-Bold", fontSize=26, textColor=WHITE,
            leading=32, alignment=TA_LEFT, spaceAfter=4),
        "subtitle": ParagraphStyle("subtitle",
            fontName="Helvetica", fontSize=11, textColor=MUTED,
            leading=16, alignment=TA_LEFT, spaceAfter=2),
        "eyebrow": ParagraphStyle("eyebrow",
            fontName="Helvetica-Bold", fontSize=7, textColor=GOLD,
            leading=10, alignment=TA_LEFT, spaceAfter=6,
            charSpace=2),
        "section": ParagraphStyle("section",
            fontName="Helvetica-Bold", fontSize=14, textColor=WHITE,
            leading=18, alignment=TA_LEFT, spaceBefore=14, spaceAfter=6),
        "body": ParagraphStyle("body",
            fontName="Helvetica", fontSize=9, textColor=TEXT,
            leading=14, alignment=TA_LEFT),
        "body_muted": ParagraphStyle("body_muted",
            fontName="Helvetica", fontSize=8, textColor=MUTED,
            leading=12, alignment=TA_LEFT),
        "mono": ParagraphStyle("mono",
            fontName="Courier", fontSize=8, textColor=MUTED,
            leading=11, alignment=TA_LEFT),
        "verdict": ParagraphStyle("verdict",
            fontName="Helvetica-Bold", fontSize=16, textColor=WHITE,
            leading=20, alignment=TA_LEFT),
        "tag": ParagraphStyle("tag",
            fontName="Helvetica-Bold", fontSize=7, textColor=GOLD,
            leading=10, charSpace=1),
        "footer": ParagraphStyle("footer",
            fontName="Helvetica", fontSize=7, textColor=MUTED,
            leading=10, alignment=TA_CENTER),
        "kpi_val": ParagraphStyle("kpi_val",
            fontName="Helvetica-Bold", fontSize=20, textColor=WHITE,
            leading=24, alignment=TA_CENTER),
        "kpi_label": ParagraphStyle("kpi_label",
            fontName="Helvetica-Bold", fontSize=6, textColor=MUTED,
            leading=9, alignment=TA_CENTER, charSpace=1),
        "kpi_sub": ParagraphStyle("kpi_sub",
            fontName="Helvetica", fontSize=7, textColor=MUTED,
            leading=10, alignment=TA_CENTER),
    }

def gold_rule():
    return HRFlowable(width="100%", thickness=0.5, color=GOLD, spaceAfter=10, spaceBefore=10)

def dark_rule():
    return HRFlowable(width="100%", thickness=0.5, color=BORDER, spaceAfter=8, spaceBefore=8)

def kpi_table(items, s):
    """items = list of (label, value, sub, accent_color)"""
    cell_w = (W - 60*mm) / len(items)
    cells = []
    for label, value, sub, accent in items:
        cell = [
            Paragraph(label.upper(), s["kpi_label"]),
            Spacer(1, 4),
            Paragraph(value, s["kpi_val"]),
            Spacer(1, 2),
            Paragraph(sub, s["kpi_sub"]),
        ]
        cells.append(cell)

    t = Table([cells], colWidths=[cell_w]*len(items))
    borders = []
    for i, (_, _, _, accent) in enumerate(items):
        borders += [
            ("BACKGROUND", (i, 0), (i, 0), SURFACE),
            ("BOX",        (i, 0), (i, 0), 0.5, BORDER),
            ("LINEABOVE",  (i, 0), (i, 0), 2,   accent),
            ("TOPPADDING", (i, 0), (i, 0), 10),
            ("BOTTOMPADDING", (i, 0), (i, 0), 10),
            ("LEFTPADDING",   (i, 0), (i, 0), 8),
            ("RIGHTPADDING",  (i, 0), (i, 0), 8),
            ("VALIGN",     (i, 0), (i, 0), "TOP"),
        ]
    t.setStyle(TableStyle(borders))
    return t

def insight_rows(items, s):
    """items = list of (tag_text, tag_color, body_text)"""
    rows = []
    for tag_txt, tag_col, body in items:
        tag_p = Paragraph(tag_txt, ParagraphStyle("t", fontName="Helvetica-Bold",
            fontSize=6, textColor=tag_col, leading=9, charSpace=1))
        body_p = Paragraph(body, s["body"])
        row = Table([[tag_p, body_p]], colWidths=[18*mm, W - 60*mm - 18*mm])
        row.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), SURFACE),
            ("BOX",        (0,0), (-1,-1), 0.5, BORDER),
            ("VALIGN",     (0,0), (-1,-1), "MIDDLE"),
            ("TOPPADDING", (0,0), (-1,-1), 7),
            ("BOTTOMPADDING", (0,0), (-1,-1), 7),
            ("LEFTPADDING",   (0,0), (0,0), 8),
            ("LEFTPADDING",   (1,0), (1,0), 8),
            ("RIGHTPADDING",  (0,0), (-1,-1), 8),
        ]))
        rows.append(row)
        rows.append(Spacer(1, 3))
    return rows

def action_rows(actions, s):
    rows = []
    for i, action in enumerate(actions, 1):
        num_p  = Paragraph(f"{i:02d}", ParagraphStyle("n", fontName="Courier-Bold",
            fontSize=8, textColor=GOLD, leading=11))
        body_p = Paragraph(action, s["body"])
        row = Table([[num_p, body_p]], colWidths=[12*mm, W - 60*mm - 12*mm])
        row.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#0d0d12")),
            ("LINEBELOW",  (0,0), (-1,-1), 0.4, BORDER),
            ("VALIGN",     (0,0), (-1,-1), "MIDDLE"),
            ("TOPPADDING", (0,0), (-1,-1), 7),
            ("BOTTOMPADDING", (0,0), (-1,-1), 7),
            ("LEFTPADDING",   (0,0), (-1,-1), 8),
            ("RIGHTPADDING",  (0,0), (-1,-1), 8),
        ]))
        rows.append(row)
        rows.append(Spacer(1, 2))
    return rows

def cost_table(breakdown, cost_impact, s):
    header = ["Commodity", "Live Price", "Hist. Avg", "Change %", "Weight", "Impact %"]
    data   = [header]
    for commodity, info in breakdown.items():
        data.append([
            commodity.replace("_", " ").title(),
            f"${info['live_price']:.2f}",
            f"${info['historical_avg']:.2f}",
            f"{info['change_pct']:+.1f}%",
            f"{info['weight']:.0%}",
            f"{info['weighted_impact']:+.2f}%",
        ])
    data.append(["", "", "", "", "TOTAL IMPACT", f"{cost_impact:+.1f}%"])

    col_w = (W - 60*mm) / 6
    t = Table(data, colWidths=[col_w*1.4, col_w*0.9, col_w*0.9, col_w*0.9, col_w*0.9, col_w*1.0])
    style = TableStyle([
        ("BACKGROUND",    (0,0), (-1,0),  SURFACE),
        ("BACKGROUND",    (0,1), (-1,-2), SURFACE2),
        ("BACKGROUND",    (0,-1),(-1,-1), DARK),
        ("TEXTCOLOR",     (0,0), (-1,0),  GOLD),
        ("TEXTCOLOR",     (0,1), (-1,-2), TEXT),
        ("TEXTCOLOR",     (0,-1),(-1,-1), GOLD),
        ("FONTNAME",      (0,0), (-1,0),  "Helvetica-Bold"),
        ("FONTNAME",      (0,-1),(-1,-1), "Helvetica-Bold"),
        ("FONTNAME",      (0,1), (-1,-2), "Helvetica"),
        ("FONTSIZE",      (0,0), (-1,-1), 8),
        ("ROWBACKGROUNDS",(0,1), (-1,-2), [SURFACE, SURFACE2]),
        ("GRID",          (0,0), (-1,-1), 0.3, BORDER),
        ("TOPPADDING",    (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
        ("ALIGN",         (1,0), (-1,-1), "CENTER"),
        ("ALIGN",         (0,0), (0,-1),  "LEFT"),
    ])
    t.setStyle(style)
    return t

# ── Main export function ───────────────────────────────────────────────────────
def generate_pdf(pr: dict, mae_values: dict = None) -> bytes:
    """
    pr = prediction_result dict from session state
    mae_values = optional {target: mae} for confidence intervals
    Returns bytes of the PDF.
    """
    result        = pr["result"]
    baseline      = pr["baseline"]
    cost_impact   = pr["cost_impact"]
    breakdown     = pr["breakdown"]
    translation   = pr["translation"]
    business_type = pr["business_type"]
    scenario_name = pr["scenario_name"]
    verdict_text, verdict_desc, verdict_color_hex = translation["verdict"]
    insights      = translation["insights"]
    actions       = translation["actions"]

    verdict_color = colors.HexColor(verdict_color_hex) if verdict_color_hex.startswith("#") else GREEN

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=30*mm, rightMargin=30*mm,
        topMargin=20*mm, bottomMargin=20*mm,
    )

    s    = styles()
    story = []
    now  = datetime.now().strftime("%d %B %Y  ·  %H:%M")

    # ── COVER HEADER ──────────────────────────────────────────────────────────
    header_data = [[
        Paragraph("BIZSHOCK", ParagraphStyle("brand", fontName="Helvetica-Bold",
            fontSize=18, textColor=GOLD, leading=22, charSpace=3)),
        Paragraph(f"Generated:  {now}", ParagraphStyle("r", fontName="Helvetica",
            fontSize=7, textColor=MUTED, leading=10, alignment=TA_RIGHT)),
    ]]
    header_t = Table(header_data, colWidths=[(W-60*mm)*0.6, (W-60*mm)*0.4])
    header_t.setStyle(TableStyle([
        ("VALIGN",  (0,0), (-1,-1), "MIDDLE"),
        ("LINEBELOW",(0,0),(-1,-1), 0.5, GOLD),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
    ]))
    story.append(header_t)
    story.append(Spacer(1, 14))

    # ── TITLE ─────────────────────────────────────────────────────────────────
    story.append(Paragraph("ECONOMIC SHOCK IMPACT REPORT", s["eyebrow"]))
    story.append(Paragraph(f"Scenario:  {scenario_name}", s["title"]))
    story.append(Paragraph(f"Business:  {business_type}  ·  Commodity exposure analysis with live market data", s["subtitle"]))
    story.append(Spacer(1, 10))
    story.append(gold_rule())

    # ── VERDICT ───────────────────────────────────────────────────────────────
    story.append(Paragraph("OVERALL ASSESSMENT", s["eyebrow"]))
    verdict_icon = "● TOUGH TIMES AHEAD" if "Tough" in verdict_text else "● PROCEED WITH CAUTION" if "Caution" in verdict_text else "● FAVORABLE CONDITIONS"
    story.append(Paragraph(verdict_icon, ParagraphStyle("verd", fontName="Helvetica-Bold",
        fontSize=15, textColor=verdict_color, leading=20, spaceAfter=6)))
    story.append(Paragraph(verdict_desc, s["body"]))
    story.append(Spacer(1, 12))
    story.append(dark_rule())

    # ── MACRO PREDICTIONS ─────────────────────────────────────────────────────
    story.append(Paragraph("MACRO INDICATOR FORECAST", s["eyebrow"]))
    story.append(Paragraph("Predicted Economic Conditions", s["section"]))

    targets_list = list(result.keys())
    kpi_items = []
    for target in targets_list:
        value = result[target]
        diff  = value - baseline[target]
        is_bad = (diff > 0 and target != "GDP Growth (% Annual)") or (diff < 0 and target == "GDP Growth (% Annual)")
        accent = RED if is_bad else GREEN
        arrow  = "▲" if diff > 0 else "▼"
        label  = target.split("(")[0].strip()
        mae    = mae_values.get(target, None) if mae_values else None
        sub    = f"{arrow} {abs(diff):.2f} pp vs baseline"
        if mae:
            sub += f"   ±{mae:.1f}%"
        kpi_items.append((label, f"{value:.1f}%", sub, accent))

    story.append(kpi_table(kpi_items, s))
    story.append(Spacer(1, 10))

    # confidence note
    if mae_values:
        story.append(Paragraph(
            "Note:  ± ranges indicate model MAE (mean absolute error). "
            "Predictions are directional guidance, not precise point forecasts.",
            s["body_muted"]))
    story.append(Spacer(1, 10))
    story.append(dark_rule())

    # ── COST IMPACT ───────────────────────────────────────────────────────────
    story.append(Paragraph("INPUT COST ANALYSIS", s["eyebrow"]))
    story.append(Paragraph("Commodity Cost Impact Breakdown", s["section"]))
    if breakdown:
        story.append(cost_table(breakdown, cost_impact, s))
    story.append(Spacer(1, 10))
    story.append(dark_rule())

    # ── INSIGHTS ──────────────────────────────────────────────────────────────
    story.append(Paragraph("RISK SIGNALS", s["eyebrow"]))
    story.append(Paragraph("Key Market Indicators", s["section"]))
    parsed_insights = []
    for insight in insights:
        if "🔴" in insight:
            tag, col = "RISK",   RED
        elif "🟡" in insight:
            tag, col = "WATCH",  AMBER
        else:
            tag, col = "STABLE", GREEN
        text = insight[2:].strip().replace("**", "")
        parsed_insights.append((tag, col, text))
    story.extend(insight_rows(parsed_insights, s))
    story.append(Spacer(1, 10))
    story.append(dark_rule())

    # ── ACTIONS ───────────────────────────────────────────────────────────────
    story.append(Paragraph("ACTION PLAN", s["eyebrow"]))
    story.append(Paragraph("Recommended Strategic Actions", s["section"]))
    parsed_actions = [a[2:].strip() for a in actions]
    story.extend(action_rows(parsed_actions, s))
    story.append(Spacer(1, 14))
    story.append(gold_rule())

    # ── FOOTER ────────────────────────────────────────────────────────────────
    story.append(Paragraph(
        "This report was generated by BizShock — an AI-powered commodity shock impact analyzer. "
        "Predictions are based on a Random Forest model trained on historical macroeconomic data "
        f"(R² > 0.90 across all indicators). Generated on {now}. "
        "Not financial advice.",
        s["footer"]))

    # ── Build ──────────────────────────────────────────────────────────────────
    def on_page(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(DARK)
        canvas.rect(0, 0, W, H, fill=1, stroke=0)
        # gold top bar
        canvas.setFillColor(GOLD)
        canvas.rect(0, H - 3, W, 3, fill=1, stroke=0)
        # page number
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(MUTED)
        canvas.drawCentredString(W/2, 10*mm, f"Page {doc.page}")
        canvas.restoreState()

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    buf.seek(0)
    return buf.read()
