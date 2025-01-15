from fastapi import APIRouter, HTTPException
from app.service import fetch_video_info, transcription_statuses

router = APIRouter()

@router.get("/video-info/{video_id}")
async def get_video_info(video_id: str):
    """
    Fetch video metadata and transcript information.
    Returns video details along with the transcription status.
    """
    try:
        video_info = fetch_video_info(video_id)        
        return video_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

