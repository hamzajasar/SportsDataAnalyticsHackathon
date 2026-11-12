"""Placeholder analytics service. Replace with topic-specific logic."""

import numpy as np
import pandas as pd

from app.schemas import DataPoint, SampleStats


def sample_stats() -> SampleStats:
    rng = np.random.default_rng(42)
    df = pd.DataFrame(
        {"label": [f"Week {i}" for i in range(1, 11)], "value": rng.normal(50, 10, 10)}
    )
    df["value"] = df["value"].round(1)
    return SampleStats(
        title="Sample metric over time",
        points=[DataPoint(**row) for row in df.to_dict("records")],
    )
