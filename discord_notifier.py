import pandas as pd
from datetime import datetime
import requests
import glob
import os

# --- CONFIGURATION ---
WEBHOOK_URL = "https://discord.com/api/webhooks/1478749174282457269/w4FgKIwgJsVg3ZgKCZU2fIlakgk--hHRHH8ojIFvSgkbyDAMRWXVaoCcq8og0lLk9DYv"
SCORE_THRESHOLD = 90

def send_to_discord(content, embeds=None):
    """Helper function to send messages to Discord via Webhook"""
    data = {"content": content}
    if embeds:
        data["embeds"] = embeds
    
    response = requests.post(WEBHOOK_URL, json=data)
    if response.status_code not in [200, 204]:
        print(f"Failed to send to Discord: {response.status_code}, {response.text}")

def main():
    # Get today's date in the exact format used in your pipeline
    today_str = datetime.now().strftime("%Y-%m-%d")
    output_dir = "output"
    
    print("Sending pipeline completion status to Discord...")
    # 1. Send the initial "Run done" message
    send_to_discord(f"✅ **Job Match Pipeline Run Done** ({today_str})")

    # Find all matched master files in case you use different models
    master_files = glob.glob(os.path.join(output_dir, "matched_master_*.csv"))
    high_match_jobs = []

    # 2. Extract matching jobs
    for file in master_files:
        try:
            df = pd.read_csv(file)
            
            # Verify the required columns exist
            if 'match_score' in df.columns and 'processed_date' in df.columns:
                
                # Force match_score to numeric in case it was saved as text
                df['match_score'] = pd.to_numeric(df['match_score'], errors='coerce')
                
                # Filter for > 90 score AND processed today
                recent_high_matches = df[
                    (df['match_score'] > SCORE_THRESHOLD) & 
                    (df['processed_date'] == today_str)
                ]
                
                # Add to our list
                for _, row in recent_high_matches.iterrows():
                    high_match_jobs.append(row)
                    
        except Exception as e:
            print(f"Error reading {file}: {e}")
    
    # 3. Send the results
    if not high_match_jobs:
        send_to_discord("ℹ️ No new jobs found today with a match score > 90.")
        return

    send_to_discord(f"🚨 **Found {len(high_match_jobs)} highly matched jobs! Recommending immediate review.**")

    # 4. Send each job as a formatted Discord "Embed"
    for job in high_match_jobs:
        company = str(job.get('company', 'Unknown Company'))
        title = str(job.get('title', 'Unknown Title'))
        score = job.get('match_score', 0)
        url = str(job.get('job_url', 'No URL'))
        location = str(job.get('location', 'Unknown Location'))
        
        # Basic URL validation for Discord embeds
        valid_url = url if url.startswith('http') else None
        
        embed = {
            "title": f"[{score}%] {title} @ {company}",
            "url": valid_url,
            "color": 5814783,  # Discord blurple color
            "fields": [
                {"name": "Location", "value": location, "inline": True},
                {"name": "Score", "value": f"{score}%", "inline": True}
            ]
        }
        
        # Send the embed. Sending them one by one bypasses Discord's character limits for large lists.
        send_to_discord("", embeds=[embed])
        
    print("Discord notification sent successfully!")

if __name__ == "__main__":
    # Ensure the requests library is available (it should be since jobspy uses it)
    main()