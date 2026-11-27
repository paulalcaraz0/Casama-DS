"""Download the Filipino Family Income and Expenditure (FIES) dataset from Kaggle.

Reusable entry point: other scripts, notebooks, or a future backend can call
`load_fies()` to get a pandas DataFrame without caring where the file came from.

Setup (one time):
  1. Kaggle -> Settings -> API -> "Create New Token" (downloads kaggle.json)
  2. mv ~/Downloads/kaggle.json ~/.kaggle/kaggle.json && chmod 600 ~/.kaggle/kaggle.json

Usage:
  python ds/fetch_data.py          # downloads into ds/data/raw/
"""

from __future__ import annotations

import sys
from pathlib import Path

DATASET = "grosvenpaul/family-income-and-expenditure"
RAW_DIR = Path(__file__).resolve().parent / "data" / "raw"


def download(force: bool = False) -> Path:
    """Download and unzip the dataset; returns the path to the CSV."""
    existing = sorted(RAW_DIR.glob("*.csv"))
    if existing and not force:
        return existing[0]

    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
    except ImportError:
        sys.exit("Kaggle package missing. Run: pip install -r ds/requirements.txt")

    api = KaggleApi()
    api.authenticate()  # reads ~/.kaggle/kaggle.json or KAGGLE_USERNAME/KAGGLE_KEY
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    api.dataset_download_files(DATASET, path=str(RAW_DIR), unzip=True, quiet=False)

    csvs = sorted(RAW_DIR.glob("*.csv"))
    if not csvs:
        sys.exit(f"No CSV found in {RAW_DIR} after download.")
    return csvs[0]


def load_fies(force: bool = False):
    """Return the FIES data as a pandas DataFrame (downloads on first use)."""
    import pandas as pd

    return pd.read_csv(download(force))


if __name__ == "__main__":
    path = download(force="--force" in sys.argv)
    df = load_fies()
    print(f"Saved: {path}")
    print(f"Shape: {df.shape[0]:,} households x {df.shape[1]} columns")
    print("Columns:")
    for col in df.columns:
        print(f"  - {col}")
