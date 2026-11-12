"""Read-only explorer over files in data/raw (works for any provided dataset)."""

from fastapi import APIRouter, HTTPException, Query

from app.schemas import DatasetInfo, DatasetPreview, DatasetSummary
from app.services import datasets as svc

router = APIRouter(prefix="/datasets", tags=["datasets"])


@router.get("", response_model=list[DatasetInfo], operation_id="listDatasets")
def list_datasets() -> list[DatasetInfo]:
    return [
        DatasetInfo(id=d.id, name=d.path.name, format=d.format, size_bytes=d.size_bytes)
        for d in svc.list_datasets()
    ]


@router.get("/preview", response_model=DatasetPreview, operation_id="previewDataset")
def preview_dataset(
    id: str,
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    sort: str | None = None,
    desc: bool = False,
) -> DatasetPreview:
    try:
        return DatasetPreview(**svc.preview(id, limit=limit, offset=offset, sort=sort, desc=desc))
    except KeyError:
        raise HTTPException(404, f"Dataset not found: {id}") from None
    except ValueError as e:
        raise HTTPException(400, str(e)) from None


@router.get("/summary", response_model=DatasetSummary, operation_id="summarizeDataset")
def summarize_dataset(id: str) -> DatasetSummary:
    try:
        return DatasetSummary(**svc.summarize(id))
    except KeyError:
        raise HTTPException(404, f"Dataset not found: {id}") from None
