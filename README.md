# YouTube Info Service

This Python-based microservice is responsible for fetching YouTube video information, including transcripts, using the [YouTube Transcript API](https://pypi.org/project/youtube-transcript-api/) and FastAPI. This service is part of a larger architecture aimed at enhancing video-based learning experiences by providing real-time access to video metadata and content.

## Features
- Fetch video metadata (title, description, channel) using the YouTube API.
- Retrieve transcripts (captions) of YouTube videos.
- Integrates with the larger microservice architecture for processing video information and AI-based learning tools.

## Tech Stack
- **FastAPI**: Python web framework for building APIs.
- **YouTube Transcript API**: Python library for retrieving YouTube video transcripts.
- **Uvicorn**: ASGI server for running FastAPI applications.
- **Python 3.9+**: Core language for the backend logic.

## Prerequisites
Make sure you have the following installed:
- Python 3.9 or higher
- `pip` (Python package installer)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/AnasKhan0607/Youtube-Learning-Mode-Info-Service.git
cd Youtube-Learning-Mode-Info-Service
```

2. Create a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```
(Windows): .\venv\Scripts\Activate

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up your `.env` file:

Create a `.env` file in the root of the project and add your environment variables (e.g., API keys):

```bash
YOUTUBE_API_KEY=your_youtube_api_key
```

## Running the Service

Run the FastAPI app using Uvicorn:

```bash
uvicorn app.main:app --reload
```

This will start the server at `http://127.0.0.1:8000`. You can access the API documentation at `http://127.0.0.1:8000/docs`.

### Running with Docker

To build and run the service using Docker:

```bash
docker build -t youtube-info-service .
docker run -p 8000:8000 youtube-info-service
```

Or, if you are using Docker Compose with other services:

```bash
docker-compose up --build
```

This will start the service along with other microservices in a shared network.

### Integration with Main Backend

This service is designed to be called by the Main Backend service, which orchestrates API requests and responses between this service, the AI service, and the video processing service. Ensure that the `youtube-info-service` is running and accessible by the backend at `http://youtube-info-service:8000` when running within the Docker network.

## API Endpoints

### 1. Fetch Video Information and Transcript

**GET** `/video-info/{video_id}`

- Fetches metadata (title, description, channel) and transcript for a given YouTube video.

#### Example Request:

```bash
curl -X GET "http://127.0.0.1:8000/video-info/X9fSMGkjtug"
```

#### Example Response:

```json
{
  "title": "i built a Raspberry Pi SUPER COMPUTER!! // ft. Kubernetes (k3s cluster w/ Rancher)",
  "description": "ENTER TO WIN a custom Raspberry Pi (pre-built with K3s)...",
  "channel": "NetworkChuck",
  "transcript": [
    "0.16: okay i went a little crazy in this video",
    "3.52: wait what's the smell",
    "6.72: oh i think it's ready come on let's go",
    "9.92: yeah yeah it's done come on come on yeah",
    "13.28: we're gonna do the slide see y'all down",
    "16.27: [Music]",
    "19.92: all right come on i don't want to burn",
    "21.279: it let's go oh",
    "24.16: oh oh yeah there it is",
    "28.56: oh it smells so good my fresh raspberry",
    "32.0: pies this is my baby 16",
    "35.2: cores 56 gigs of ram this is my",
    "38.079: raspberry pi",
    "38.879: super computer"
  ]
}
```

### 2. Health Check 

**GET** `/health`

- This endpoint checks the health of the service.

## Project Structure

```
/app
    ├── /routes.py      # Defines the API routes
    ├── /service.py    # Handles external service calls like YouTube API, Transcript API
    ├── /schemas.py     # Defines the data models and response formats
    └── /main.py        # Entry point for the FastAPI service
```

## Future Enhancements
- Add support for more languages in transcript fetching.
- Improve transcript processing to handle different formatting options (e.g., SRT, VTT).
- Integrate additional YouTube features such as comments, likes, and related video recommendations.

## Contributing
Contributions are welcome! Please open a pull request or create an issue to discuss the changes you'd like to make.
