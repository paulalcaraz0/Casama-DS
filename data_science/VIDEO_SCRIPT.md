# Video Script — Casama Bill Pulse

Format modelled on ASEAN Data Science Explorers entries: problem → data → analysis →
insights → recommendation → impact. Target length about 5–7 minutes. Show the dashboard
on screen for each finding. Figures are from the October 2026 PSA release; if you re-run
the script before recording, read the new values off the dashboard.

---

## 1. Hook (0:00–0:30)
**On screen:** a Casama Bill Tracker screen with a split electricity bill.

> "Four housemates, one electricity bill, and it's higher than last month again. Who saw
> that coming? In shared living, money fights rarely start with rent. They start with the
> bill nobody could predict."

## 2. The problem (0:30–1:15)
**On screen:** the dashboard's *The problem* section; Casama feature list.

- Introduce Casama, built by our 3rd-year partners: presence, deliveries, chores, and a
  Bill Tracker for rent, water, electricity, LPG and internet.
- A split works when everyone knows what's coming. Our question: **which shared bills rise
  fastest, which jump without warning, and do the jumps follow a pattern?**
- Link to SDG 11 (sustainable cities and communities) and SDG 1 (poverty: household cost
  pressure on renters and students).

## 3. The data (1:15–2:15)
**On screen:** *The data* section; terminal running `python3 casama_bills_analysis.py`.

- Source: **PSA OpenSTAT API**, the official Consumer Price Index, monthly since 2018,
  354 items, every region and province. Free, no key.
- We mapped every Casama bill category to a CPI item (show the mapping table).
- Pipeline: query → clean → analyse → reuse. Show the script pulling live data.
- Second table from the same API: 2023 Family Income and Expenditure Survey.
- Why an API: it updates every month, so the app can use it, not just this report.

## 4. Findings (2:15–4:45)

**Finding 1 — Rising faster than prices overall (≈40s).**
Metro Manila since Jan 2018: LPG **+120.6%**, electricity **+69.3%**, water **+60.6%**,
against **+38.0%** for all items. Rent **+26.0%** and internet **+3.0%** grew slower than inflation.

**Finding 2 — Unpredictability (≈45s). This is the key finding.**
Electricity moved by 2% or more in **54 of 105 months**; LPG in **48**. Rent: **1**.
Internet: **0**. Utilities are the bills that surprise a household.

**Finding 3 — Calendar pattern (≈35s).**
Water tends to jump in **January (+6.78% on average)**, electricity in **July (+2.22%)**.
Caveat on screen: each month averages only 8–9 years, so it's a tendency, not a forecast.

**Finding 4 — Who feels it (≈30s).**
Metro Manila families spend **28.8%** of their budget on housing and utilities, against
**22.9%** nationally. City renters, Casama's main users, are the most exposed.

## 5. Recommendation: what Casama can build (4:45–6:00)
**On screen:** the *Try it* estimator. Type ₱3,000 electricity for July and show the
range. Then the four recommendation cards.

1. **Price pulse** on each bill: flag a bill that rose much more than the regional index.
2. **Heads-up reminders** before high-risk months (water in January, electricity in July).
3. **Buffer for unpredictable bills:** fixed split for rent and internet, a small shared
   buffer for electricity and LPG.
4. **Monthly refresh** as a Supabase scheduled function using the same PSA query, by region.

## 6. Impact and close (6:00–6:30)
> "Casama already keeps the household organised. With public data, it can also tell
> housemates what's coming before the bill arrives. Fewer surprises, fairer splits,
> calmer homes."

Credits: team names, the Casama team, data from the Philippine Statistics Authority.

---

### Limits to mention if asked
- CPI measures price change, not peso amounts or how much a household uses.
- "Gas" in CPI is household fuel gas, mainly LPG.
- Electricity in NCR mostly follows one distributor's rate changes.
- The estimator is a prototype; the app should combine it with each household's own bills.
