"""
Draw the README charts as SVG files (GitHub renders them inline).
Reads ./output/*.csv written by casama_bills_analysis.py. Standard library only.

    python3 make_charts.py
"""
from __future__ import annotations

import csv
from html import escape
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / "output"
CHARTS = HERE / "charts"
NCR = "National Capital Region (NCR)"
PH = "PHILIPPINES"

# Casama brand colors (lib/core/constants/colors.dart)
CORAL, TEAL, NAVY, MUTED, GRID, INK, SUB = ("#E87968", "#3F7772", "#1C2E4A",
                                           "#9EABB2", "#E4E9E7", "#1C2E4A", "#607078")
SERIES = {"Gas (LPG)": CORAL, "Electricity": "#F4B544", "Water": TEAL,
          "Rent": NAVY, "Internet": "#52677D", "All items (inflation)": MUTED}
FONT = "font-family='Inter, Segoe UI, Helvetica, Arial, sans-serif'"


def read(name: str) -> list[dict]:
    with open(OUT / name, newline="") as f:
        return list(csv.DictReader(f))


def svg(w: int, h: int, body: list[str], title: str, subtitle: str) -> str:
    head = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{w}' height='{h}' viewBox='0 0 {w} {h}' {FONT}>",
            f"<title>{escape(title)}</title>",
            f"<rect width='{w}' height='{h}' fill='#FFFFFF' rx='10'/>",
            f"<text x='24' y='34' font-size='17' font-weight='600' fill='{INK}'>{escape(title)}</text>",
            f"<text x='24' y='56' font-size='12.5' fill='{SUB}'>{escape(subtitle)}</text>"]
    return "\n".join(head + body + ["</svg>"])


def text(x, y, s, size=12, fill=INK, anchor="start", weight="400"):
    return (f"<text x='{x:.1f}' y='{y:.1f}' font-size='{size}' fill='{fill}' "
            f"text-anchor='{anchor}' font-weight='{weight}'>{escape(str(s))}</text>")


def hbar_chart(rows, title, subtitle, fmt, colors, legend=None, w=760):
    """rows: [(label, [values...])], one bar per value."""
    n_per = len(rows[0][1])
    bar_h, gap_in, gap_out = 16, 4, 14
    top, left, right = 84 + (22 if legend else 0), 170, 110
    h = top + len(rows) * (n_per * bar_h + (n_per - 1) * gap_in + gap_out) + 16
    vmax = max(v for _, vs in rows for v in vs)
    vmin = min(0, min(v for _, vs in rows for v in vs))
    span = (w - left - right)
    sx = lambda v: left + (v - vmin) / (vmax - vmin) * span
    body = []
    if legend:
        x = 24
        for name, col in legend:
            body.append(f"<rect x='{x}' y='68' width='12' height='12' rx='2' fill='{col}'/>")
            body.append(text(x + 18, 78.5, name, 12, SUB))
            x += 30 + len(name) * 7
    body.append(f"<line x1='{sx(0):.1f}' x2='{sx(0):.1f}' y1='{top - 6}' y2='{h - 14}' stroke='{GRID}'/>")
    y = top
    for label, vs in rows:
        block = n_per * bar_h + (n_per - 1) * gap_in
        body.append(text(left - 12, y + block / 2 + 4, label, 12.5, INK, "end"))
        for i, v in enumerate(vs):
            x0, x1 = sorted((sx(0), sx(v)))
            col = colors(label, i)
            body.append(f"<rect x='{x0:.1f}' y='{y}' width='{max(1, x1 - x0):.1f}' height='{bar_h}' rx='3' fill='{col}'/>")
            body.append(text(x1 + 8, y + bar_h - 4, fmt(v), 12, INK if i == 0 else SUB))
            y += bar_h + gap_in
        y += gap_out - gap_in
    return svg(w, h, body, title, subtitle)


def line_chart(cpi, w=760, h=380):
    cats = list(SERIES)
    data = {c: [(r["period"], float(r["value"])) for r in cpi
                if r["geo"] == NCR and r["casama_category"] == c] for c in cats}
    periods = [p for p, _ in data["All items (inflation)"]]
    vals = [v for c in cats for _, v in data[c]]
    lo, hi = (min(vals) // 20) * 20, (max(vals) // 20 + 1) * 20
    left, right, top, bottom = 52, 150, 76, 40
    sx = lambda i: left + i / (len(periods) - 1) * (w - left - right)
    sy = lambda v: top + (hi - v) / (hi - lo) * (h - top - bottom)
    body = []
    v = lo
    while v <= hi:
        body.append(f"<line x1='{left}' x2='{w - right}' y1='{sy(v):.1f}' y2='{sy(v):.1f}' stroke='{GRID}'/>")
        body.append(text(left - 8, sy(v) + 4, int(v), 11, SUB, "end"))
        v += 20
    for i, p in enumerate(periods):
        if p.endswith("-01") and int(p[:4]) % 2 == 0:
            body.append(text(sx(i), h - bottom + 18, p[:4], 11, SUB, "middle"))
    ends = []
    for c in cats:
        pts = " ".join(f"{sx(i):.1f},{sy(v):.1f}" for i, (_, v) in enumerate(data[c]))
        dash = " stroke-dasharray='5 4'" if c.startswith("All") else ""
        body.append(f"<polyline points='{pts}' fill='none' stroke='{SERIES[c]}' stroke-width='2.2'{dash}/>")
        last = data[c][-1][1]
        ends.append([sy(last), c, last])
    ends.sort()
    for i in range(1, len(ends)):  # keep end labels apart
        ends[i][0] = max(ends[i][0], ends[i - 1][0] + 15)
    for y, c, last in ends:
        body.append(text(w - right + 8, y + 4, f"{c.replace(' (inflation)', '')} {last:.0f}", 11.5, SERIES[c], weight="600"))
    return svg(w, h, body, "Price index by bill, Metro Manila (2018 = 100)",
               f"Monthly PSA CPI, {periods[0]} to {periods[-1]}. Dashed line: all items.")


def heatmap(season, w=760):
    cats = ["Electricity", "Gas (LPG)", "Water", "Rent", "Internet"]
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    val = {(r["category"], r["month"]): float(r["avg_mom_pct"]) for r in season if r["geo"] == NCR}
    vmax = max(abs(val[(c, m)]) for c in cats for m in months)
    left, top, cw, ch = 120, 92, (w - 120 - 24) / 12, 34
    h = int(top + len(cats) * ch + 40)
    body = [text(left + cw * (i + .5), top - 10, m, 11.5, SUB, "middle") for i, m in enumerate(months)]
    for j, c in enumerate(cats):
        body.append(text(left - 12, top + j * ch + ch / 2 + 4, c, 12.5, INK, "end"))
        for i, m in enumerate(months):
            v = val[(c, m)]
            a = min(1, abs(v) / vmax) * .85 + .06
            col = "216,74,58" if v >= 0 else "56,142,60"
            x, y = left + i * cw, top + j * ch
            body.append(f"<rect x='{x + 1.5:.1f}' y='{y + 1.5:.1f}' width='{cw - 3:.1f}' height='{ch - 3:.1f}' rx='3' fill='rgba({col},{a:.2f})'/>")
            body.append(text(x + cw / 2, y + ch / 2 + 4, "0.0" if round(v, 1) == 0 else f"{v:+.1f}", 11, "#FFFFFF" if a > .5 else INK, "middle"))
    body.append(text(24, h - 14, "Red: prices usually rise that month. Green: they usually ease. About 8 to 9 years per cell.", 11.5, SUB))
    return svg(w, h, body, "Average month-to-month price change by calendar month (%)",
               "Metro Manila, 2018 to 2026, PSA CPI")


def main():
    CHARTS.mkdir(exist_ok=True)
    summ = read("summary.csv")
    get = lambda geo, cat, f: float(next(r[f] for r in summ if r["geo"] == geo and r["category"] == cat))
    cats = ["Gas (LPG)", "Electricity", "Water", "All items (inflation)", "Restock (cleaning)",
            "Rent", "Appliance repair", "Internet", "Courier / delivery"]

    growth = [(c.replace(" (inflation)", ""), [get(NCR, c, "cumulative_pct"), get(PH, c, "cumulative_pct")]) for c in cats]
    (CHARTS / "1_growth.svg").write_text(hbar_chart(
        growth, "Price change since January 2018, by Casama bill category",
        "PSA CPI, change from Jan 2018 to the latest month", lambda v: f"{v:+.1f}%",
        lambda label, i: (CORAL if i == 0 else "#F3B8AE") if label != "All items" else (NAVY if i == 0 else MUTED),
        legend=[("Metro Manila", CORAL), ("Philippines", "#F3B8AE")]))

    (CHARTS / "2_trend.svg").write_text(line_chart(read("cpi_monthly.csv")))

    vol = sorted(((c.replace(" (inflation)", ""), [get(NCR, c, "share_months_2pct_jump")]) for c in cats),
                 key=lambda r: -r[1][0])
    n = int(get(NCR, "Electricity", "months_compared"))
    (CHARTS / "3_volatility.svg").write_text(hbar_chart(
        vol, "How often each bill jumps: months with a 2%+ price change",
        f"Metro Manila, share of {n} month-to-month changes since Feb 2018",
        lambda v: f"{v:.1f}%  ({round(v * n / 100)} of {n})",
        lambda label, i: MUTED if label == "All items" else CORAL))

    (CHARTS / "4_seasonality.svg").write_text(heatmap(read("seasonality.csv")))

    bud = read("fies_budget.csv")
    names = {"Food and Non-Alcoholic Beverages": "Food",
             "Housing, Water, Electricity, Gas and Other Fuels": "Housing & utilities",
             "Transport": "Transport", "Information and Communication": "Phone & internet",
             "Furnishings and Routine Household Maintenance": "Household upkeep"}
    bget = lambda reg, g: float(next(r["share_pct"] for r in bud if r["region"] == reg and r["group"] == g))
    rows = [(short, [bget("NATIONAL CAPITAL REGION", g), bget("PHILIPPINES", g)]) for g, short in names.items()]
    (CHARTS / "5_budget.svg").write_text(hbar_chart(
        rows, "Share of family spending, 2023", "PSA Family Income and Expenditure Survey 2023, Table 7",
        lambda v: f"{v:.1f}%", lambda label, i: TEAL if i == 0 else "#A9C9C6",
        legend=[("Metro Manila", TEAL), ("Philippines", "#A9C9C6")]))

    print("Wrote", ", ".join(sorted(p.name for p in CHARTS.glob("*.svg"))))


if __name__ == "__main__":
    main()
