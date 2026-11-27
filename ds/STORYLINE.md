# Casama DS — Presentation Storyline (ASEAN Data Science Explorers format)

> **Status: draft.** Every `[TBD]` is a number we fill in **after** running the EDA.
> Do not present any number that the notebook did not produce.

**Title:** *Affordable Shared Living — What Filipino Households Really Spend, and How to Split It Fairly*
**Dataset:** Filipino Family Income and Expenditure Survey (PSA FIES, via Kaggle), ~41k households.
**Supporting data:** ASEANstats / World Bank (CPI, urbanisation) for the ASEAN comparison.
**Target length:** 8–10 minutes + 5 minutes judge Q&A.

---

## Slide-by-slide

| # | Slide | What we say | Visual |
|---|---|---|---|
| 1 | **Title + team** | Team name, school, topic in one line. | Casama logo + owl mascot |
| 2 | **The problem** | Rising cost of living; more Filipinos (students, young workers) share homes to afford rent and bills. Shared costs cause conflict when splits feel unfair. | 1 striking stat + photo |
| 3 | **Why it matters (ASEAN link)** | Ties to **SDG 1** (No Poverty), **SDG 11** (Sustainable Cities), **ASEAN Socio-Cultural Community Blueprint 2025** (quality of life, poverty reduction). | SDG icons |
| 4 | **Data & method** | Source, size, cleaning steps, EDA process (univariate → bivariate → segment comparison). | Pipeline diagram |
| 5 | **Key insight 1 — Where the money goes** | Food and housing/water take `[TBD]%` of household spending; the share is `[TBD]` higher for the lowest income decile. | Stacked bar by income decile |
| 6 | **Key insight 2 — Sharing saves, per person** | Per-person spending on housing/water and food falls by `[TBD]%` from 1–2 member to 5+ member households → sharing is efficient. | Line: per-capita cost vs household size |
| 7 | **Key insight 3 — Where you live matters** | NCR households spend `[TBD]×` more per person on housing than `[lowest region]`. | Map or ranked bar by region |
| 8 | **Key insight 4 — Who is most burdened** | Renters / low-income / large-family households spend `[TBD]%` of income on essentials. | Box plot by tenure status |
| 9 | **Key insight 5 — ASEAN context** | Philippine CPI / food inflation vs neighbours `[TBD]`. | Multi-country line chart |
| 10 | **Our solution — Casama Insights** | Live demo: in-app dashboard compares *your* household's bills to similar FIES households (same region + size) and suggests a fair split. | Screen recording |
| 11 | **Recommendations (by stakeholder)** | **Government:** target utility/food subsidies using regional burden data. **Landlords / businesses:** transparent per-unit utility billing. **Households / citizens:** track and split bills with tools like Casama; budget against regional benchmarks. | 3-column slide |
| 12 | **Impact & scaling** | Same pipeline works for any ASEAN country with a household expenditure survey; dashboard reads a precomputed JSON so it is cheap to update. | ASEAN map |
| 13 | **Limitations** | FIES is survey data (self-reported, one survey year); housing & water combined; no direct electricity bill column (verify). | Bullet list |
| 14 | **References + closing line** | Data sources, SDG/ASEAN docs. Closing line e.g. *"Fair homes start with clear numbers."* | — |

---

## Likely judge questions (prepare answers)

Based on the questions asked in the 2021 Regional Finals (fit with ASEAN agenda, feasibility, scaling across the system).

1. **How does this fit the ASEAN agenda, and how can ASEAN support you?**
   → SDG 1/11 and the ASCC Blueprint; ASEAN could promote harmonised household-expenditure data so the dashboard extends to other member states.
2. **Your data is from one survey year. Is it still valid today?**
   → Patterns (shares, per-capita economies of scale) are structural; absolute pesos can be adjusted with CPI (slide 9). Pipeline re-runs on the next FIES release.
3. **Why should someone trust the "fair split" suggestion?**
   → It is based on ~41k real households in the same region and size, and the user can see the benchmark behind it.
4. **How did you clean the data / handle outliers?**
   → Describe exact steps from the notebook (missing values, income outliers, per-capita normalisation).
5. **Correlation is not causation — how do you know household size causes lower costs?**
   → We claim association, controlled within region/income groups; we do not claim causation.
6. **How would you scale beyond the Philippines?**
   → Swap the data source in `ds/fetch_data.py`; the app reads one summary JSON per country.
7. **What is the business / sustainability model for Casama?**
   → Free core app; insights feature is a differentiator; (team to decide).
8. **Privacy — does the app send our bills anywhere?**
   → Comparison runs on-device against a bundled summary; no personal data leaves the phone.

---

## Presentation tips from the reference video

- Number the insights out loud ("Our first key insight…") — the finalists did this.
- **Every insight = one statistic + one chart + one sentence of meaning.**
- Recommendations split by **government / businesses / citizens**.
- Cite ASEAN frameworks by name; judges noticed this.
- End with a references slide and a short memorable line.
