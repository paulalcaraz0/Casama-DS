# Casama DS — Data Science Final Project

Exploratory Data Analysis of Filipino household spending, presented in the
**ASEAN Data Science Explorers** format and surfaced inside the Casama app as an
analytics dashboard.

- **Dataset:** [Filipino Family Income and Expenditure](https://www.kaggle.com/datasets/grosvenpaul/family-income-and-expenditure) (PSA FIES, Kaggle)
- **Question:** What do Filipino households spend on essentials, how does sharing a home change the cost per person, and how can shared households split costs fairly?
- **Storyline / pitch plan:** [STORYLINE.md](STORYLINE.md)

## Structure

```
ds/
  fetch_data.py        reusable loader (Kaggle API) -> load_fies()
  requirements.txt
  data/raw/            downloaded CSV (git-ignored)
  notebooks/           EDA notebooks          (next step)
  results/             figures + findings.md  (next step)
assets/ds/summary.json precomputed stats for the in-app Insights screen (next step)
lib/features/insights/ Insights dashboard UI                          (next step)
```

## Setup

```bash
cd ds
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Kaggle API token: kaggle.com -> Settings -> API -> Create New Token
mkdir -p ~/.kaggle && mv ~/Downloads/kaggle.json ~/.kaggle/ && chmod 600 ~/.kaggle/kaggle.json

python fetch_data.py   # downloads the CSV and prints its columns
```

## EDA process

1. **Data understanding:** shape, column types, units (annual pesos).
2. **Cleaning:** missing values, duplicates, outliers in income and spending, per-capita columns.
3. **Univariate:** distributions of income and each expense category.
4. **Bivariate:** expense vs income, expense vs household size, correlation heatmap.
5. **Segments:** region, tenure status (owner and renter), income decile, household type.
6. **Findings:** 4–5 key insights, each with one statistic and one chart (see STORYLINE.md).
7. **Export:** summary JSON for the app dashboard.

## Related repos

- Casama app (3rd-year Application Development): this codebase
- Casama AI (AI final project): https://github.com/JohnAlcaraz02/Casama-AI
