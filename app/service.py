# app/services.py

import requests
import os
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3/videos"

def fetch_video_info(video_id: str):
    video_info = get_video_details(video_id)
    transcript = fetch_video_transcript(video_id)
    
    video_info["transcript"] = transcript
    return video_info

def get_video_details(video_id: str):
    params = {
        'id': video_id,
        'key': YOUTUBE_API_KEY,
        'part': 'snippet'
    }
    
    response = requests.get(YOUTUBE_API_URL, params=params)
    
    if response.status_code != 200:
        raise Exception(f"Failed to fetch video info: {response.status_code}, {response.text}")

    data = response.json()
    
    if 'items' not in data or len(data['items']) == 0:
        raise Exception("No video found")
    
    video_snippet = data['items'][0]['snippet']
    
    return {
        'title': video_snippet['title'],
        'description': video_snippet['description'],
        'channel': video_snippet['channelTitle']
    }

def fetch_video_transcript(video_id: str):
    try:
        proxies = {
            "https": "socks5://torproxy:9050",
            "http": "socks5://torproxy:9050",
        }
        transcript = YouTubeTranscriptApi.get_transcript(video_id, proxies=proxies)
        formatted_transcript = format_transcript(transcript)
        return formatted_transcript
    except NoTranscriptFound:
        return "No transcript found for this video."
    except TranscriptsDisabled:
        return "Transcripts are disabled for this video."

def format_transcript(transcript):
    return [
        f"{entry['start']}: {entry['text']}" for entry in transcript
    ]
