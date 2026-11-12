import numpy as np
import pandas as pd
import pytest

from app.core.config import settings


@pytest.fixture
def sample_data_dir(tmp_path, monkeypatch):
    """Temporary data/ dir with small sports-like datasets in several formats."""
    raw = tmp_path / "raw"
    (raw / "nested").mkdir(parents=True)
    rng = np.random.default_rng(0)
    teams = pd.DataFrame({"team_id": [1, 2, 3, 4], "team_name": ["Lions", "Bears", "Owls", None]})
    matches = pd.DataFrame(
        {
            "match_id": range(1, 21),
            "date": pd.date_range("2024-01-01", periods=20, freq="7D"),
            "home_team_id": rng.integers(1, 5, 20),
            "away_team_id": rng.integers(1, 5, 20),
            "home_goals": rng.poisson(1.5, 20),
            "away_goals": rng.poisson(1.2, 20).astype(float),
        }
    )
    matches.loc[3, "away_goals"] = np.nan
    teams.to_csv(raw / "teams.csv", index=False)
    matches.to_parquet(raw / "nested" / "Matches 2024.parquet", index=False)
    teams.to_excel(raw / "teams_excel.xlsx", index=False)
    (raw / "notes.txt").write_text("ignored")
    monkeypatch.setattr(settings, "data_dir", tmp_path)
    return tmp_path
