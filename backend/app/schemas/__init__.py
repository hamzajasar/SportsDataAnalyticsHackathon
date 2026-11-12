from typing import Any

from pydantic import BaseModel


class Health(BaseModel):
    status: str
    database: bool


class DataPoint(BaseModel):
    label: str
    value: float


class SampleStats(BaseModel):
    title: str
    points: list[DataPoint]


class DatasetInfo(BaseModel):
    id: str
    name: str
    format: str
    size_bytes: int


class DatasetPreview(BaseModel):
    columns: list[str]
    rows: list[list[Any]]
    total_rows: int


class ColumnSummary(BaseModel):
    name: str
    type: str
    null_pct: float
    approx_unique: int
    min: str | None
    max: str | None
    mean: float | None
    likely_key: bool


class DatasetSummary(BaseModel):
    dataset_id: str
    rows: int
    columns: list[ColumnSummary]
