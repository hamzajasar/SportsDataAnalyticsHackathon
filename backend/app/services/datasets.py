"""Generic, read-only access to whatever datasets are dropped into data/raw/.

Used by the data-explorer API, `make profile` and `make seed`. Works for any topic.
"""

import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import duckdb
import pandas as pd

from app.core.config import settings

SUPPORTED = {".csv", ".tsv", ".parquet", ".json", ".jsonl", ".ndjson", ".xlsx", ".xls"}
COMPRESSED = {".gz"}  # e.g. games.csv.gz (DuckDB reads these directly)


def _format(p: Path) -> str | None:
    """'games.csv.gz' -> 'csv', 'x.parquet' -> 'parquet', unsupported -> None."""
    suffixes = [s.lower() for s in p.suffixes]
    if suffixes and suffixes[-1] in COMPRESSED:
        suffixes = suffixes[:-1]
    if suffixes and suffixes[-1] in SUPPORTED:
        return suffixes[-1].lstrip(".")
    return None


def raw_dir() -> Path:
    return settings.data_dir / "raw"


@dataclass(frozen=True)
class DatasetFile:
    id: str  # path relative to data/raw, posix style, e.g. "matches/2024.csv"
    path: Path
    format: str
    size_bytes: int


def list_datasets() -> list[DatasetFile]:
    root = raw_dir()
    if not root.exists():
        return []
    files = []
    for p in sorted(root.rglob("*")):
        fmt = _format(p) if p.is_file() else None
        if fmt and not p.name.startswith("."):
            files.append(
                DatasetFile(
                    id=p.relative_to(root).as_posix(),
                    path=p,
                    format=fmt,
                    size_bytes=p.stat().st_size,
                )
            )
    return files


def get_dataset(dataset_id: str) -> DatasetFile:
    """Look up by id. Only files discovered under data/raw are allowed (no path traversal)."""
    for d in list_datasets():
        if d.id == dataset_id:
            return d
    raise KeyError(dataset_id)


def table_name(dataset_id: str) -> str:
    """'Matches/2024 Season.csv' -> 'matches_2024_season' (also strips .csv.gz)."""
    stem = re.sub(r"(\.[A-Za-z0-9]+)?\.(gz)$", "", dataset_id)
    stem = stem.rsplit(".", 1)[0] if _format(Path(dataset_id)) else stem
    name = re.sub(r"[^0-9a-zA-Z]+", "_", stem).strip("_").lower()
    return name if name and not name[0].isdigit() else f"t_{name}"


@lru_cache(maxsize=8)
def _excel_df(path: str, mtime: float) -> pd.DataFrame:
    return pd.read_excel(path)


def relation(con: duckdb.DuckDBPyConnection, d: DatasetFile) -> duckdb.DuckDBPyRelation:
    """DuckDB relation over the file (lazy; handles large files without loading into memory)."""
    p = str(d.path)
    match d.format:
        case "csv" | "tsv":
            return con.read_csv(p)
        case "parquet":
            return con.read_parquet(p)
        case "json" | "jsonl" | "ndjson":
            return con.read_json(p)
        case _:  # excel
            return con.from_df(_excel_df(p, d.path.stat().st_mtime))


def _records(df: pd.DataFrame) -> list[list[Any]]:
    # Round-trip through pandas JSON to turn NaN/NaT/timestamps/numpy types into JSON-safe values
    return json.loads(df.to_json(orient="values", date_format="iso", default_handler=str))


def preview(
    dataset_id: str,
    limit: int = 50,
    offset: int = 0,
    sort: str | None = None,
    desc: bool = False,
) -> dict[str, Any]:
    d = get_dataset(dataset_id)
    con = duckdb.connect()
    rel = relation(con, d)
    columns = rel.columns
    total = rel.aggregate("count(*)").fetchall()[0][0]
    if sort is not None:
        if sort not in columns:
            raise ValueError(f"Unknown column: {sort}")
        rel = rel.order(f'"{sort.replace(chr(34), chr(34) * 2)}" {"DESC" if desc else "ASC"}')
    df = rel.limit(limit, offset).df()
    return {"columns": columns, "rows": _records(df), "total_rows": total}


def summarize(dataset_id: str) -> dict[str, Any]:
    """Per-column stats (type, nulls, distinct, min/max/mean) via DuckDB SUMMARIZE."""
    d = get_dataset(dataset_id)
    con = duckdb.connect()
    rel = relation(con, d)
    total = rel.aggregate("count(*)").fetchall()[0][0]
    s = con.sql("SUMMARIZE SELECT * FROM rel").df()
    cols = []
    for r in s.to_dict("records"):
        null_pct = float(r["null_percentage"]) if pd.notna(r["null_percentage"]) else 0.0
        approx_unique = int(r["approx_unique"]) if pd.notna(r["approx_unique"]) else 0
        cols.append(
            {
                "name": r["column_name"],
                "type": r["column_type"],
                "null_pct": round(null_pct, 2),
                "approx_unique": approx_unique,
                "min": None if pd.isna(r["min"]) else str(r["min"]),
                "max": None if pd.isna(r["max"]) else str(r["max"]),
                "mean": None if pd.isna(r["avg"]) else _to_float(r["avg"]),
                "likely_key": total > 0 and null_pct == 0 and approx_unique >= total * 0.95,
            }
        )
    return {"dataset_id": d.id, "rows": total, "columns": cols}


def _to_float(v: Any) -> float | None:
    try:
        return round(float(v), 4)
    except (TypeError, ValueError):
        return None


def load_df(dataset_id: str) -> pd.DataFrame:
    """Load an entire dataset into pandas."""
    d = get_dataset(dataset_id)
    con = duckdb.connect()
    return relation(con, d).df()
