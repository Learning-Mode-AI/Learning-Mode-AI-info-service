# app/services.py

import time
import boto3
import json
import yt_dlp
import requests
import os
import tempfile
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3/videos"

SMARTPROXY_USER = os.getenv("SMARTPROXY_USER")
SMARTPROXY_PASS = os.getenv("SMARTPROXY_PASS")
SMARTPROXY_HOST = os.getenv("SMARTPROXY_HOST", "gate.smartproxy.com")
SMARTPROXY_PORT = os.getenv("SMARTPROXY_PORT", "10001")

# Define proxy settings
PROXIES = {
    "http": f"http://{SMARTPROXY_USER}:{SMARTPROXY_PASS}@{SMARTPROXY_HOST}:{SMARTPROXY_PORT}",
    "https": f"http://{SMARTPROXY_USER}:{SMARTPROXY_PASS}@{SMARTPROXY_HOST}:{SMARTPROXY_PORT}",
}

def fetch_video_info(video_id: str):
    # Step 1: Get video details
    video_info = get_video_details(video_id)
    
    # Step 2: Fetch transcript
    try:
        transcript = fetch_video_transcript(video_id)  # This returns a formatted transcript
        video_info["transcript"] = transcript
    except Exception as e:
        print(f"Error fetching transcript: {e}")
        video_info["transcript"] = "Transcript could not be fetched."


    # Return the combined video info
    return video_info

def get_video_details(video_id: str):
    params = {
        'id': video_id,
        'key': YOUTUBE_API_KEY,
        'part': 'snippet'
    }
    
    response = requests.get(YOUTUBE_API_URL, params=params, proxies=PROXIES, timeout=10)
    
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

transcription_statuses = {}
def fetch_video_transcript(video_id: str):
    try:
        # Attempt to fetch the YouTube transcript
        transcript = YouTubeTranscriptApi.get_transcript(video_id, proxies=PROXIES)
        formatted_transcript = format_transcript(transcript)
        return formatted_transcript

    except (NoTranscriptFound, TranscriptsDisabled):
        print(f"No YouTube transcript available for video ID: {video_id}. Falling back to audio transcription.")
        try:    
            audio_file = download_audio(video_id)
            print(f"Downloaded audio file: {audio_file}")

            if not os.path.exists(audio_file):
                raise Exception(f"Audio file not found: {audio_file}")

            bucket_name = "learningmodeai-transcription"
            s3_uri = upload_to_s3(audio_file, bucket_name)

            job_name = f"transcription-{video_id}-{int(time.time())}"
            print(f"Starting transcription job with name: {job_name}")
            transcript_result = transcribe_audio(job_name, s3_uri)

            formatted_transcript = process_transcription_result(transcript_result)
            return formatted_transcript

        except Exception as e:
            print(f"Error during fallback transcription: {e}")
            raise Exception(f"Failed to fetch transcript via fallback: {e}")

        
def process_transcription_result(transcript_result):
    """
    Process the raw transcript result from Amazon Transcribe
    and format it into grouped segments.
    """
    transcript_items = transcript_result.get("results", {}).get("items", [])
    grouped_transcript = []
    current_segment = []
    current_start_time = None

    for item in transcript_items:
        if item.get("type") == "pronunciation":
            word = item.get("alternatives", [{}])[0].get("content", "")
            start_time = item.get("start_time", None)

            if current_start_time is None:
                current_start_time = start_time

            current_segment.append(word)

            if len(current_segment) >= 5:
                segment_text = " ".join(current_segment)
                grouped_transcript.append(f"{current_start_time}: {segment_text}")
                current_segment = []
                current_start_time = None

    if current_segment:
        segment_text = " ".join(current_segment)
        grouped_transcript.append(f"{current_start_time}: {segment_text}")

    print("Formatted Transcript:", grouped_transcript)
    return grouped_transcript
           
def download_audio(video_id: str):
    # Get the current working directory
    current_dir = os.getcwd()
    output_path = os.path.join(current_dir, f"{video_id}.mp3")  # Intended file path

    # yt-dlp options
    ydl_opts = {
        'format': 'bestaudio/best',  # Download the best available audio format
        'outtmpl': output_path,  # Save the file at the specified path
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',  # Use FFmpeg to extract audio
            'preferredcodec': 'mp3',  # Convert the audio to MP3 format
        }],
    }

    try:
        # Download the audio
        print(f"Downloading audio to: {output_path}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=True)
        
        # yt-dlp appends another .mp3 extension; account for this
        final_path = output_path if os.path.exists(output_path) else f"{output_path}.mp3"

        if not os.path.exists(final_path):
            raise Exception(f"File was not created: {final_path}")

        print(f"File created: {final_path}")
        return final_path
    except Exception as e:
        raise Exception(f"Failed to download audio: {e}")

    
def upload_to_s3(file_path, bucket_name, object_name=None):
    """
    Upload a file to an S3 bucket.
    
    Args:
        file_path (str): Path to the file to upload.
        bucket_name (str): Name of the S3 bucket.
        object_name (str): S3 object name. If not specified, file_path is used.

    Returns:
        str: The S3 URI of the uploaded file.
    """
    if object_name is None:
        object_name = os.path.basename(file_path)

    s3_client = boto3.resource('s3')
    try:
        for bucket in s3_client.buckets.all():
            print(bucket.name)
        with open(file_path, 'rb') as body:
            s3_client.Bucket('learningmodeai-transcription').put_object(Key=object_name, Body = body)
        file_uri = f"s3://{bucket_name}/{object_name}"
        print(f"File uploaded to: {file_uri}")
        
        # Remove the local file after upload
        os.remove(file_path)
        print(f"Local file deleted: {file_path}")
        
        return file_uri
    except Exception as e:
        raise Exception(f"Failed to upload file to S3: {e}")

def transcribe_audio(job_name, file_uri, region_name="us-east-2"):
    """
    Start a transcription job using Amazon Transcribe.
    
    Args:
        job_name (str): Unique name for the transcription job.
        file_uri (str): S3 URI of the audio file.
        region_name (str): AWS region for the Transcribe service.

    Returns:
        dict: Transcription result as a JSON object.
    """
    transcribe_client = boto3.client("transcribe", region_name=region_name)

    try:
        # Start the transcription job
        transcribe_client.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={"MediaFileUri": file_uri},
            MediaFormat="mp3",
            LanguageCode="en-US"
        )

        # Wait for the job to complete
        while True:
            response = transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
            status = response["TranscriptionJob"]["TranscriptionJobStatus"]
            if status in ["COMPLETED", "FAILED"]:
                print(f"Transcription job status: {status}")
                if status == "COMPLETED":
                    transcript_uri = response["TranscriptionJob"]["Transcript"]["TranscriptFileUri"]
                    transcript_response = requests.get(transcript_uri)
                    return transcript_response.json()  # Return the transcription JSON
                else:
                    raise Exception("Transcription job failed.")
            print("Waiting for transcription job to complete...")
            time.sleep(5)
    except Exception as e:
        raise Exception(f"Failed to transcribe audio: {e}")

def format_transcript(transcript):
    return [
        f"{entry['start']}: {entry['text']}" for entry in transcript
    ]
