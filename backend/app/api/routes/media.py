from fastapi import APIRouter, File, UploadFile

from app.schemas.common import Message

router = APIRouter()


@router.post("/upload", response_model=Message)
async def upload_media(file: UploadFile = File(...)):
    # Placeholder: save to S3/local in real impl
    return Message(message=f"received upload: filename={file.filename} content_type={file.content_type}")


@router.get("/{media_id}", response_model=Message)
def download_media(media_id: str):
    # Placeholder: should return StreamingResponse / Redirect to presigned url
    return Message(message=f"placeholder download for media_id={media_id}")
