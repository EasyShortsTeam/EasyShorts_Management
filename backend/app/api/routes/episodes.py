from fastapi import APIRouter, Depends, HTTPException

from app.core.security import require_admin
from app.schemas.episodes import Episode, EpisodeCreate, EpisodeUpdate
from app.services.mock_store import store

router = APIRouter(dependencies=[Depends(require_admin)])


@router.get("", response_model=list[Episode])
def list_episodes():
    return [Episode(**e) for e in store.episodes]


@router.post("", response_model=Episode)
def create_episode(payload: EpisodeCreate):
    new = {
        "id": f"e_{len(store.episodes)+1:03d}",
        "series_id": payload.series_id,
        "title": payload.title,
        "status": "ready",
    }
    store.episodes.append(new)
    return Episode(**new)


@router.get("/{episode_id}", response_model=Episode)
def get_episode(episode_id: str):
    for e in store.episodes:
        if e["id"] == episode_id:
            return Episode(**e)
    raise HTTPException(status_code=404, detail="episode not found")


@router.put("/{episode_id}", response_model=Episode)
def update_episode(episode_id: str, payload: EpisodeUpdate):
    for e in store.episodes:
        if e["id"] == episode_id:
            if payload.title is not None:
                e["title"] = payload.title
            if payload.status is not None:
                e["status"] = payload.status
            return Episode(**e)
    raise HTTPException(status_code=404, detail="episode not found")
