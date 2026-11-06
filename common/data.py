"""Helpers for loading shared sample datasets."""
from pathlib import Path

import pandas as pd

SAMPLE_DIR = Path(__file__).resolve().parent.parent / "data" / "sample"

HOURS_PER_MONTH = 730

DEPARTMENT_BUDGETS = {
    "Development": 1000,
    "E-commerce": 3000,
    "Analytics": 1500,
    "Customer Services": 800,
    "IT Operations": 700,
}


def load_sample(name: str) -> pd.DataFrame:
    """Load data/sample/<name>.csv."""
    return pd.read_csv(SAMPLE_DIR / f"{name}.csv")
