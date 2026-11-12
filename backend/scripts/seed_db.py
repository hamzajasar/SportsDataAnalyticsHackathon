"""Load every dataset in data/raw into Postgres as `raw_<name>` tables (replaces existing).

Usage: make seed            (all files)
       make seed f="teams.csv"  (one file)
Use when you want SQL over the data in Postgres, or for a deployed backend that has no data/ dir.
Tables prefixed `raw_` are ignored by Alembic (see migrations/env.py).
"""

import sys

from sqlalchemy import text

from app.db.session import engine
from app.services import datasets as svc

CHUNK = 50_000


def seed(file_id: str) -> None:
    d = svc.get_dataset(file_id)
    table = f"raw_{svc.table_name(d.id)}"
    df = svc.load_df(d.id)
    df.columns = [str(c) for c in df.columns]
    with engine.begin() as conn:
        conn.execute(text(f'DROP TABLE IF EXISTS "{table}"'))
    df.to_sql(table, engine, index=False, chunksize=CHUNK, method="multi")
    print(f"  {d.id:<45} -> {table} ({len(df):,} rows)")


def main() -> None:
    ids = sys.argv[1:] or [d.id for d in svc.list_datasets()]
    if not ids:
        print(f"No datasets found in {svc.raw_dir()}")
        return
    print("Seeding Postgres:")
    for i in ids:
        seed(i)


if __name__ == "__main__":
    main()
