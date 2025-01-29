import os
import json

DATA_DIR = "data"
TRANSCRIPTS_DIR = os.path.join(DATA_DIR, "transcripts")

transcript_file = os.path.join(TRANSCRIPTS_DIR, "H6LHhUzRJEc.json")
transcript_outfile = transcript_file.split('.')[0] + '_minute.json'

with open(transcript_file, "r") as f:
    transcript = json.load(f)

# Initialize variables for grouping
grouped_transcript = []
text = ""
current_start = transcript[0]["start"]

# Iterate through the transcript
for entry in transcript:
    if entry["start"] < current_start + 60:
        # Add entry to the current group
        text += (entry["text"] + " ")
    else:
        # Save the current group and start a new one
        grouped_transcript.append(
            {
                "start": current_start,
                "text": text
            }
        )
        current_start = entry["start"]
        text = entry["text"] + " "

grouped_transcript.append(
    {
        "start": current_start,
        "text": text
    }
)

# Save the grouped transcript
with open(transcript_outfile, "w") as f:
    json.dump(grouped_transcript, f, indent=4)

print("Transcript grouped and saved as grouped_transcript.json.")
