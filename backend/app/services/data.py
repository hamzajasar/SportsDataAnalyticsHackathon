"""Notebook helpers: cache cleaned data to data/processed and run ad-hoc SQL.

To load provided datasets use `app.services.datasets.load_df`.
"""

from pathlib import Path

import duckdb
import pandas as pd

from app.core.config import settings

PROCESSED = settings.data_dir / "processed"


def save_processed(df: pd.DataFrame, name: str) -> Path:
    """Save a cleaned DataFrame to data/processed/<name>.parquet (fast to reload)."""
    PROCESSED.mkdir(parents=True, exist_ok=True)
    path = PROCESSED / f"{name}.parquet"
    df.to_parquet(path, index=False)
    return path


def load_processed(name: str) -> pd.DataFrame:
    return pd.read_parquet(PROCESSED / f"{name}.parquet")


def sql(query: str) -> pd.DataFrame:
    """Run SQL with DuckDB directly over files, e.g.
    sql("SELECT team, avg(points) FROM 'data/raw/games.csv' GROUP BY team")
    """
    return duckdb.sql(query).df()
