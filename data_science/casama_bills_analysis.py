"""
Casama x PSA: how fast are shared-household bills rising, and which ones
are hard to predict?

Pulls live data from the PSA OpenSTAT API, then writes to ./output/:
    cpi_monthly.csv        tidy monthly CPI for every Casama bill category
    summary.csv            growth, YoY, volatility, peak month per category
    seasonality.csv        average month-on-month change by calendar month
    fies_budget.csv    2023 NCR household spending on bill-related groups
    findings.json          everything above, for the dashboard

Re-run any time; new PSA months appear automatically.
    python casama_bills_analysis.py            # default: Philippines + NCR
    python casama_bills_analysis.py "Region VII (Central Visayas)"
"""
from __future__ import annotations

import csv
import json
import statistics as st
import sys
from pathlib import Path

import psa_client as psa

# Casama BillCategory / feature  ->  PSA CPI commodity code (label prefix)
CASAMA_TO_CPI = {
    "All items (inflation)": "0 - ALL ITEMS",
    "Rent": "04.1.1.0",
    "Water": "04.4.1.1",
    "Electricity": "04.5.1.0",
    "Gas (LPG)": "04.5.2",
    "Internet": "08.3.3.0",
    "Appliance repair": "05.3.3.0",
    "Restock (cleaning)": "05.6.1.1",
    "Courier / delivery": "07.4.1",
}

OUT = Path(__file__).parent / "output"


def pct(a: float, b: float) -> float:
    return (b / a - 1) * 100


def analyse(series: list[float], periods: list[str]) -> dict:
    mom = [pct(series[i - 1], series[i]) for i in range(1, len(series))]
    yoy = [pct(series[i - 12], series[i]) for i in range(12, len(series))]
    by_month: dict[str, list[float]] = {m: [] for m in psa.MONTHS}
    for i in range(1, len(series)):
        by_month[psa.MONTHS[int(periods[i][5:]) - 1]].append(mom[i - 1])
    season = {m: round(st.mean(v), 3) for m, v in by_month.items() if v}
    peak = max(season, key=season.get)
    big_jumps = sum(1 for x in mom if abs(x) >= 2)
    return {
        "start": periods[0], "end": periods[-1],
        "start_value": series[0], "end_value": series[-1],
        "cumulative_pct": round(pct(series[0], series[-1]), 1),
        "latest_yoy_pct": round(yoy[-1], 1),
        "avg_yoy_pct": round(st.mean(yoy), 1),
        "mom_volatility": round(st.pstdev(mom), 2),
        "months_compared": len(mom),
        "months_with_2pct_jump": big_jumps,
        "share_months_2pct_jump": round(big_jumps / len(mom) * 100, 1),
        "peak_month": peak,
        "peak_month_avg_mom_pct": season[peak],
        "seasonality": season,
        "yoy": [{"period": periods[i], "value": round(yoy[i - 12], 2)}
                for i in range(12, len(series))],
    }


def fies_budget(regions=("NATIONAL CAPITAL REGION", "PHILIPPINES")) -> list[dict]:
    """2023 FIES: share (%) of family spending per group. In this PSA table the
    group rows are already percentages of total; the total row is in PHP millions."""
    groups = ["Housing, Water, Electricity, Gas and Other Fuels",
              "Information and Communication",
              "Furnishings and Routine Household Maintenance",
              "Food and Non-Alcoholic Beverages", "Transport"]
    rows = psa.query(psa.FIES_TABLE, {
        "Region, Province, and HUC": list(regions),
        "Major Expenditure Group": groups,
        "Indicator": ["All Income Groups"],
    })
    return [{"region": r["Region, Province, and HUC"],
             "group": r["Major Expenditure Group"].strip(". "),
             "share_pct": r["value"]} for r in rows]


def main(extra_geo: str | None = None) -> None:
    geos = ["PHILIPPINES", "National Capital Region (NCR)"]
    if extra_geo:
        geos.append(extra_geo)
    code_to_name = {v: k for k, v in CASAMA_TO_CPI.items()}
    rows = psa.cpi_series(geos, list(CASAMA_TO_CPI.values()))
    for r in rows:
        r["casama_category"] = next(n for c, n in code_to_name.items()
                                    if r["item"].startswith(c))

    OUT.mkdir(exist_ok=True)
    with open(OUT / "cpi_monthly.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["geo", "casama_category", "item", "period", "value"])
        w.writeheader()
        w.writerows(rows)

    findings = {"source": "PSA OpenSTAT API, " + psa.CPI_TABLE, "geos": {}}
    summary, season_rows = [], []
    for geo in dict.fromkeys(r["geo"] for r in rows):
        findings["geos"][geo] = {}
        for cat in CASAMA_TO_CPI:
            sub = [r for r in rows if r["geo"] == geo and r["casama_category"] == cat]
            if len(sub) < 13:
                continue
            a = analyse([r["value"] for r in sub], [r["period"] for r in sub])
            a["index"] = [{"period": r["period"], "value": r["value"]} for r in sub]
            findings["geos"][geo][cat] = a
            summary.append({"geo": geo, "category": cat,
                            **{k: v for k, v in a.items()
                               if k not in ("seasonality", "yoy", "index")}})
            season_rows += [{"geo": geo, "category": cat, "month": m, "avg_mom_pct": v}
                            for m, v in a["seasonality"].items()]

    for name, data in (("summary.csv", summary), ("seasonality.csv", season_rows)):
        with open(OUT / name, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(data[0]))
            w.writeheader()
            w.writerows(data)

    budget = fies_budget()
    findings["fies_2023"] = budget
    with open(OUT / "fies_budget.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(budget[0]))
        w.writeheader()
        w.writerows(budget)

    (OUT / "findings.json").write_text(json.dumps(findings, indent=1))

    print(f"{'geo':<32}{'category':<24}{'cum%':>8}{'YoY%':>8}{'vol':>7}  peak")
    for s in summary:
        print(f"{s['geo'][:31]:<32}{s['category']:<24}{s['cumulative_pct']:>8}"
              f"{s['latest_yoy_pct']:>8}{s['mom_volatility']:>7}  "
              f"{s['peak_month']} ({s['peak_month_avg_mom_pct']:+.2f}%)")
    print("\n2023 household spending shares (FIES):")
    for b in budget:
        print(f"  {b['region'][:12]:<13}{b['group']:<50}{b['share_pct']:>6}%")
    print(f"\nWrote {OUT}/")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
