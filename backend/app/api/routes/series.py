from fastapi import APIRouter, HTTPException

from app.schemas.series import Series, SeriesCreate, SeriesUpdate
from app.services.mock_store import store

router = APIRouter()


@router.get("", response_model=list[Series])
def list_series():
    return [Series(**s) for s in store.series]


@router.post("", response_model=Series)
def create_series(payload: SeriesCreate):
    new = {"id": f"s_{len(store.series)+1:03d}", "title": payload.title, "description": payload.description}
    store.series.append(new)
    return Series(**new)


@router.get("/{series_id}", response_model=Series)
def get_series(series_id: str):
    for s in store.series:
        if s["id"] == series_id:
            return Series(**s)
    raise HTTPException(status_code=404, detail="series not found")


@router.put("/{series_id}", response_model=Series)
def update_series(series_id: str, payload: SeriesUpdate):
    for s in store.series:
        if s["id"] == series_id:
            if payload.title is not None:
                s["title"] = payload.title
            if payload.description is not None:
                s["description"] = payload.description
            return Series(**s)
    raise HTTPException(status_code=404, detail="series not found")
