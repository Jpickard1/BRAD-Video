"""
This file constructs a RAG database for a youtube channel.

This entails both (1) building a vectorized database compatible with LangChain and (2) organizing and processing the transcripts to later be parsed
"""
# Standard python imports
import os
import json
from tqdm import tqdm

# Scraping the youtube channel
import scrapetube
from youtube_transcript_api import YouTubeTranscriptApi

# RAG database constructor
from rag_database_constructor import build_rag_database

# Constants
DCMB_CHANNEL_ID = "UCjvLXvfPupVHtGU_ckTDPwA"
DATA_DIR = "data"
TRANSCRIPTS_DIR = os.path.join(DATA_DIR, "transcripts")
RAG_DATABASES_DIR = os.path.join(DATA_DIR, "RAG_Databases")
CHANNEL_VIDEOS_FILE = os.path.join(DATA_DIR, "dcmb_video_list.json")
DB_NAME = "rag_db"
HUGGINGFACE_MODEL = "BAAI/bge-base-en-v1.5"

# Ensure the data and transcripts directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(TRANSCRIPTS_DIR, exist_ok=True)

# Step 1: Fetch and save the video list if it doesn't exist
if not os.path.exists(CHANNEL_VIDEOS_FILE):
    videos = scrapetube.get_channel(DCMB_CHANNEL_ID)  # Fetch videos by channel ID
    video_list = []
    
    for video in tqdm(videos, desc=f"Fetching videos from channel {DCMB_CHANNEL_ID}"):
        video_list.append(video)

    # Save video list to a JSON file
    with open(CHANNEL_VIDEOS_FILE, "w") as f:
        json.dump(video_list, f, indent=4)
    print(f"Video list saved to {CHANNEL_VIDEOS_FILE}")
else:
    print(f"Video list already exists at {CHANNEL_VIDEOS_FILE}")

# Step 2: Process transcripts if they haven't been generated
transcripts_missing = not os.listdir(TRANSCRIPTS_DIR)

if transcripts_missing:
    # Load the video list
    with open(CHANNEL_VIDEOS_FILE, "r") as f:
        video_list = json.load(f)

    print(f"Processing transcripts for {len(video_list)} videos...")

    for video in tqdm(video_list, desc="Fetching transcripts"):
        video_id = video['videoId']

        try:
            # Fetch the transcript
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            
            # Create the full text transcript
            text_transcript = " ".join(segment['text'] for segment in transcript)

            # Save the raw transcript with timestamps as a JSON file
            raw_transcript_path = os.path.join(TRANSCRIPTS_DIR, f"{video_id}.json")
            with open(raw_transcript_path, "w") as f:
                json.dump(transcript, f, indent=4)

            # Save the full text transcript as a .txt file
            text_transcript_path = os.path.join(TRANSCRIPTS_DIR, f"{video_id}.txt")
            with open(text_transcript_path, "w") as f:
                f.write(text_transcript)

        except Exception as e:
            print(f"Failed to fetch transcript for video ID {video_id}: {e}")

    print("Transcripts processed and saved.")
else:
    print("Transcripts already exist. No further action required.")


# rag_databases_missing = not os.listdir(RAG_DATABASES_DIR)
rag_databases_missing = not os.path.exists(RAG_DATABASES_DIR) or not os.listdir(RAG_DATABASES_DIR)

if rag_databases_missing:
    build_rag_database(
        transcripts_dir=TRANSCRIPTS_DIR,
        db_name=DB_NAME,
        db_path=RAG_DATABASES_DIR,
        huggingface_model=HUGGINGFACE_MODEL,
        chunk_size=1000,
        chunk_overlap=200,
        verbose=True
    )

    print("RAG database processed and saved.")
else:
    print("RAG database already exists. No further action required.")
