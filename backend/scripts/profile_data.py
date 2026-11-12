"""Profile every dataset in data/raw -> data/processed/_profile.md (+ console summary).

Usage: make profile
Shows size, columns, types, missing values, likely keys and probable joins between files,
so we can judge each topic's data quickly.
"""

import itertools
import re
from datetime import datetime

import duckdb

from app.core.config import settings
from app.services import datasets as svc


def human(n: int) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if n < 1024:
            return f"{n:.0f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


ID_LIKE = re.compile(r"(^id$|_id$|^id_|_key$|_code$)", re.IGNORECASE)
MAX_PAIRS = 300  # safety cap so a folder of wide files can't make this run for minutes


def _candidate_pairs(files, summaries):
    """(file_a, col_a, file_b, col_b) pairs that look joinable. Only ID-like columns count:

    - same ID-like column name in both files (`team_id` ↔ `team_id`), or
    - foreign-key style: `home_team_id` in A ends with `team_id`, a likely key in B.
    """
    cols = {f.id: summaries[f.id]["columns"] for f in files}
    seen = set()
    for a, b in itertools.permutations(files, 2):
        for ca in cols[a.id]:
            for cb in cols[b.id]:
                same = ca["name"] == cb["name"] and bool(ID_LIKE.search(ca["name"]))
                fk = (
                    not same
                    and cb["likely_key"]
                    and len(cb["name"]) > 2
                    and ca["name"].lower().endswith("_" + cb["name"].lower())
                )
                key = (a.id, ca["name"], b.id, cb["name"])
                rev = (b.id, cb["name"], a.id, ca["name"])
                if (same or fk) and key not in seen and rev not in seen:
                    seen.add(key)
                    yield a, ca["name"], b, cb["name"]


def join_hints(files, summaries) -> list[str]:
    """Probable joins between files, with % of distinct values in A found in B.

    Each (file, column) is read once into a DuckDB temp table of distinct values.
    """
    con = duckdb.connect()
    cache: dict[tuple[str, str], str] = {}

    def distinct(f, col) -> str:
        if (f.id, col) not in cache:
            name = f"d{len(cache)}"
            con.register("src", svc.relation(con, f))
            q = col.replace('"', '""')
            con.execute(
                f'CREATE TEMP TABLE {name} AS SELECT DISTINCT CAST("{q}" AS VARCHAR) v '
                f'FROM src WHERE "{q}" IS NOT NULL'
            )
            cache[(f.id, col)] = name
        return cache[(f.id, col)]

    hints = []
    for i, (a, col_a, b, col_b) in enumerate(_candidate_pairs(files, summaries)):
        if i >= MAX_PAIRS:
            hints.append(f"_…stopped after {MAX_PAIRS} candidate pairs_")
            break
        try:
            ta, tb = distinct(a, col_a), distinct(b, col_b)
            n, hit = con.sql(
                f"SELECT (SELECT count(*) FROM {ta}), "
                f"(SELECT count(*) FROM {ta} WHERE v IN (SELECT v FROM {tb}))"
            ).fetchall()[0]
            pct = 100 * hit / n if n else 0
            if pct >= 5:  # below that it's a name collision, not a join
                hints.append(
                    f"`{a.id}`.`{col_a}` → `{b.id}`.`{col_b}` — {pct:.0f}% of values match"
                )
        except Exception as e:  # unreadable column etc.
            hints.append(f"`{a.id}`.`{col_a}` → `{b.id}`.`{col_b}` — could not compare ({e})")
    return hints


def wide_format_note(summary) -> str | None:
    """Flag files whose columns look like entities (e.g. one column per player)."""
    names = [c["name"] for c in summary["columns"]]
    if len(names) < 20:
        return None
    prefixes = {}
    for n in names:
        prefixes[n.split("-")[0]] = prefixes.get(n.split("-")[0], 0) + 1
    top, count = max(prefixes.items(), key=lambda kv: kv[1])
    if count >= 10 and count / len(names) > 0.5:
        return (
            f"Wide format: {count} of {len(names)} columns start with `{top}` (one column per "
            "entity?). Unpivot to long format before analysis: `rel.unpivot(...)` / `df.melt(...)`."
        )
    return None


def main() -> None:
    files = svc.list_datasets()
    if not files:
        supported = ", ".join(sorted(svc.SUPPORTED))
        print(f"No datasets found in {svc.raw_dir()} (supported: {supported})")
        return

    summaries = {}
    lines = [f"# Data profile\n\n_Generated {datetime.now():%Y-%m-%d %H:%M}_\n"]
    lines.append("| Dataset | Format | Size | Rows | Columns | Avg missing |")
    lines.append("|---|---|---|---|---|---|")
    print(f"\n{'Dataset':<45} {'Rows':>10} {'Cols':>5} {'Missing':>8}  Size")
    for f in files:
        try:
            s = svc.summarize(f.id)
        except Exception as e:
            print(f"{f.id:<45} ERROR: {e}")
            lines.append(f"| `{f.id}` | {f.format} | {human(f.size_bytes)} | error: {e} | | |")
            continue
        summaries[f.id] = s
        miss = sum(c["null_pct"] for c in s["columns"]) / max(len(s["columns"]), 1)
        ncols = len(s["columns"])
        print(f"{f.id:<45} {s['rows']:>10,} {ncols:>5} {miss:>7.1f}%  {human(f.size_bytes)}")
        lines.append(
            f"| `{f.id}` | {f.format} | {human(f.size_bytes)} | {s['rows']:,} "
            f"| {len(s['columns'])} | {miss:.1f}% |"
        )

    for f in files:
        if f.id not in summaries:
            continue
        s = summaries[f.id]
        lines.append(f"\n## `{f.id}` — {s['rows']:,} rows\n")
        if note := wide_format_note(s):
            lines.append(f"> ⚠️ {note}\n")
        lines.append("| Column | Type | Missing % | Distinct | Min | Max | Mean | Key? |")
        lines.append("|---|---|---|---|---|---|---|---|")
        for c in s["columns"]:
            lines.append(
                f"| {c['name']} | {c['type']} | {c['null_pct']} | {c['approx_unique']:,} "
                f"| {(c['min'] or '')[:30]} | {(c['max'] or '')[:30]} "
                f"| {'' if c['mean'] is None else c['mean']} | {'✓' if c['likely_key'] else ''} |"
            )

    profiled = [f for f in files if f.id in summaries]
    hints = join_hints(profiled, summaries) if len(profiled) > 1 else []
    lines.append("\n## Probable joins\n")
    none_msg = "_None found by column name — check for differently named IDs._"
    lines += [f"- {h}" for h in hints] or [none_msg]

    out = settings.data_dir / "processed" / "_profile.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n")
    if hints:
        print("\nProbable joins:")
        for h in hints:
            print("  " + h.replace("`", ""))
    print(f"\nFull report: {out}")


if __name__ == "__main__":
    main()
