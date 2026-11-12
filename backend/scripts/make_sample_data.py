"""Generate a small fake sports dataset in data/raw/_sample/ to try the tooling before real data.

Usage: make sample-data      Remove with: make clean-sample
"""

import numpy as np
import pandas as pd

from app.core.config import settings


def main() -> None:
    out = settings.data_dir / "raw" / "_sample"
    out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(7)
    teams = pd.DataFrame(
        {
            "team_id": range(1, 9),
            "team_name": ["Lions", "Bears", "Owls", "Wolves", "Hawks", "Sharks", "Bulls", "Foxes"],
            "city": [
                "Sarajevo",
                "Mostar",
                "Tuzla",
                "Zenica",
                "Bihac",
                "Banja Luka",
                "Brcko",
                "Trebinje",
            ],
        }
    )
    n = 112
    home = rng.integers(1, 9, n)
    away = (home + rng.integers(1, 8, n) - 1) % 8 + 1
    matches = pd.DataFrame(
        {
            "match_id": range(1, n + 1),
            "date": pd.date_range("2025-08-01", periods=n, freq="2D"),
            "home_team_id": home,
            "away_team_id": away,
            "home_goals": rng.poisson(1.6, n),
            "away_goals": rng.poisson(1.1, n),
            "attendance": rng.normal(8000, 2500, n).round().clip(500),
        }
    )
    matches.loc[rng.choice(n, 6, replace=False), "attendance"] = np.nan
    players = pd.DataFrame(
        {
            "player_id": range(1, 161),
            "team_id": np.repeat(range(1, 9), 20),
            "position": rng.choice(["GK", "DF", "MF", "FW"], 160, p=[0.1, 0.35, 0.35, 0.2]),
            "age": rng.integers(17, 37, 160),
            "minutes": rng.integers(0, 3000, 160),
            "goals": rng.poisson(2, 160),
            "xg": rng.gamma(2, 1.2, 160).round(2),
        }
    )
    teams.to_csv(out / "teams.csv", index=False)
    matches.to_parquet(out / "matches.parquet", index=False)
    players.to_csv(out / "players.csv", index=False)
    print(f"Sample data written to {out}")


if __name__ == "__main__":
    main()
