# app/routes.py

from fastapi import APIRouter, HTTPException
from app.service import fetch_video_info

router = APIRouter()

@router.get("/video-info/{video_id}")
async def get_video_info(video_id: str):
    try:
        video_info = fetch_video_info(video_id)
        return video_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

