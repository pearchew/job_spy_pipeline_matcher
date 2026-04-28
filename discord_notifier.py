import pandas as pd
from datetime import datetime
import requests
import glob
import os
import re

# --- CONFIGURATION ---
WEBHOOK_URL = "https://discord.com/api/webhooks/1478749174282457269/w4FgKIwgJsVg3ZgKCZU2fIlakgk--hHRHH8ojIFvSgkbyDAMRWXVaoCcq8og0lLk9DYv"
SCORE_THRESHOLD = 90

def send_to_discord(content=None, file_path=None):
    """Helper function to send messages and files to Discord via Webhook"""
    data = {}
    if content:
        data["content"] = content
        
    # If a file path is provided and exists, upload it as an attachment
    if file_path and os.path.exists(file_path):
        with open(file_path, "rb") as f:
            # Discord requires files to be passed in a specific multipart format
            files = {"file": (os.path.basename(file_path), f)}
            response = requests.post(WEBHOOK_URL, data=data, files=files)
    else:
        # Standard JSON request if there is no file or the file doesn't exist
        response = requests.post(WEBHOOK_URL, json=data)
        
    if response.status_code not in [200, 204]:
        print(f"Failed to send to Discord: {response.status_code}, {response.text}")

def sanitize_field(val, default="Unknown"):
    """Ensures the value is a valid, non-empty string for Discord"""
    if pd.isna(val) or val is None:
        return default
    val_str = str(val).strip()
    if not val_str or val_str.lower() == "nan":
        return default
    return val_str

def main():
    today_str = datetime.now().strftime("%Y-%m-%d")
    output_dir = "output"
    
    print("Sending pipeline completion status to Discord...")
    send_to_discord(content=f"✅ **Job Match Pipeline Run Done** ({today_str})")

    master_files = glob.glob(os.path.join(output_dir, "matched_master_*.csv"))
    high_match_jobs = []

    for file in master_files:
        try:
            df = pd.read_csv(file)
            if 'match_score' in df.columns and 'processed_date' in df.columns:
                df['match_score'] = pd.to_numeric(df['match_score'], errors='coerce')
                recent_high_matches = df[
                    (df['match_score'] >= SCORE_THRESHOLD) & 
                    (df['processed_date'] == today_str)
                ]
                for _, row in recent_high_matches.iterrows():
                    high_match_jobs.append(row)
        except Exception as e:
            print(f"Error reading {file}: {e}")
    
    if not high_match_jobs:
        send_to_discord(content="ℹ️ No new jobs found today with a match score > 90.")
        return

    send_to_discord(content=f"🚨 **Found {len(high_match_jobs)} highly matched jobs! Generating resumes...**")

    for job in high_match_jobs:
        title = sanitize_field(job.get('title'), 'Unknown Title')
        company = sanitize_field(job.get('company'), 'Unknown Company')
        location = sanitize_field(job.get('location'), 'Unknown Location')
        job_id = sanitize_field(job.get('job_id'), 'NO_ID')
        
        score_val = job.get('match_score')
        score = int(score_val) if not pd.isna(score_val) else 0
        
        url_val = job.get('job_url')
        url = str(url_val).strip() if not pd.isna(url_val) else "No Link Available"
        
        # 1. Format the simple text message
        message = f"[**{title} at {company}**]({url}), {location} | Match Score: {score}% "
        
        # 2. Reconstruct the exact filename the resume_tailorer.py script used
        safe_filename_base = re.sub(r'[^\w\-_\. ]', '_', f"{job_id}_{company}_{title}")
        
        # --- THIS IS THE CRITICAL CHANGE (.md instead of .html) ---
        md_file_path = os.path.join(output_dir, "tailored_resumes", f"{safe_filename_base}.md")
        
        # 3. Send via the 'content' and 'file_path' arguments
        send_to_discord(content=message, file_path=md_file_path)
        
    print("Discord notification sent successfully!")

if __name__ == "__main__":
    main()