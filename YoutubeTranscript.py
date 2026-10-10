import sys
import json
import time
import random
from youtube_transcript_api import YouTubeTranscriptApi

# 1. Get the Video ID from the command line argument passed by n8n
try:
    if len(sys.argv) > 1:
        video_id = sys.argv[1]
    else:
        raise ValueError("No Video ID provided")

    # ==============================================================================
    # 2. ANTI-BAN DELAY (Added)
    # ==============================================================================
    # Randomly wait between 15 and 40 seconds before making the request.
    # This variation prevents the "robotic heartbeat" pattern that gets IPs banned.
    sleep_time = random.uniform(15, 40)
    
    # We print to stderr so n8n logs it but doesn't break the JSON output
    print(f"Waiting {sleep_time:.1f}s to avoid IP ban...", file=sys.stderr)
    time.sleep(sleep_time)
    
    # ==============================================================================
    # 3. Fetch the transcript
    # ==============================================================================
    ytt_api = YouTubeTranscriptApi()
    transcript_obj = ytt_api.fetch(video_id)

    # 4. Process: Join all text segments into one long string
    # This cleans it up for your "Filter" or "AI" nodes later
    full_text = " ".join([item.text for item in transcript_obj])

    # 5. Success Output: Print JSON to stdout
    # n8n will capture this single line
    output = {
        "status": "success",
        "video_id": video_id,
        "transcript": full_text
    }
    print(json.dumps(output))

except Exception as e:
    # 6. Error Output: Even if it fails, print JSON so n8n flow doesn't break
    error_output = {
        "status": "error",
        "video_id": video_id if 'video_id' in locals() else "unknown",
        "message": str(e)
    }
    print(json.dumps(error_output))