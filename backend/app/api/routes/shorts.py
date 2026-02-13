from fastapi import APIRouter, HTTPException

from app.schemas.common import Message
from app.schemas.shorts import Short, ShortCreate, ShortUpdate
from app.services.mock_store import store

router = APIRouter()


@router.get("", response_model=list[Short])
def list_shorts():
    return [Short(**s) for s in store.shorts]


@router.post("", response_model=Short)
def create_short(payload: ShortCreate):
    new = {"id": f"sh_{len(store.shorts)+1:03d}", "title": payload.title, "status": "draft"}
    store.shorts.append(new)
    return Short(**new)


@router.get("/{short_id}", response_model=Short)
def get_short(short_id: str):
    for s in store.shorts:
        if s["id"] == short_id:
            return Short(**s)
    raise HTTPException(status_code=404, detail="short not found")


@router.put("/{short_id}", response_model=Short)
def update_short(short_id: str, payload: ShortUpdate):
    for s in store.shorts:
        if s["id"] == short_id:
            if payload.title is not None:
                s["title"] = payload.title
            if payload.status is not None:
                s["status"] = payload.status
            return Short(**s)
    raise HTTPException(status_code=404, detail="short not found")


# Detail domains (placeholders)
@router.get("/{short_id}/video", response_model=Message)
def short_video(short_id: str):
    return Message(message=f"placeholder video domain for {short_id}")


@router.get("/{short_id}/story", response_model=Message)
def short_story(short_id: str):
    return Message(message=f"placeholder story domain for {short_id}")


@router.get("/{short_id}/community", response_model=Message)
def short_community(short_id: str):
    return Message(message=f"placeholder community domain for {short_id}")


@router.get("/{short_id}/ranking", response_model=Message)
def short_ranking(short_id: str):
    return Message(message=f"placeholder ranking domain for {short_id}")


@router.get("/{short_id}/choice", response_model=Message)
def short_choice(short_id: str):
    return Message(message=f"placeholder choice domain for {short_id}")


@router.get("/{short_id}/chat", response_model=Message)
def short_chat(short_id: str):
    return Message(message=f"placeholder chat domain for {short_id}")
