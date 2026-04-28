import pandas as pd
from datetime import datetime
import requests
import glob
import os

# --- CONFIGURATION ---
WEBHOOK_URL = "https://discord.com/api/webhooks/1478749174282457269/w4FgKIwgJsVg3ZgKCZU2fIlakgk--hHRHH8ojIFvSgkbyDAMRWXVaoCcq8og0lLk9DYv"
SCORE_THRESHOLD = 90

def send_to_discord(content=None, embeds=None):
    """Helper function to send messages to Discord via Webhook"""
    data = {}
    
    if content:
        data["content"] = content
        
    if embeds:
        data["embeds"] = embeds
    
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
    # 1. Send the initial "Run done" message
    send_to_discord(content=f"✅ **Job Match Pipeline Run Done** ({today_str})")

    master_files = glob.glob(os.path.join(output_dir, "matched_master_*.csv"))
    high_match_jobs = []

    # 2. Extract matching jobs
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
    
    # 3. Send the results
    if not high_match_jobs:
        send_to_discord(content="ℹ️ No new jobs found today with a match score > 90.")
        return

    send_to_discord(content=f"🚨 **Found {len(high_match_jobs)} highly matched jobs! Recommending immediate review.**")

    # 4. Send each job as a formatted plain text message
    for job in high_match_jobs:
        # Safely clean and extract data
        title = sanitize_field(job.get('title'), 'Unknown Title')
        company = sanitize_field(job.get('company'), 'Unknown Company')
        location = sanitize_field(job.get('location'), 'Unknown Location')
        
        # Safely handle the score, defaulting to 0 if missing
        score_val = job.get('match_score')
        score = int(score_val) if not pd.isna(score_val) else 0
        
        url_val = job.get('job_url')
        url = str(url_val).strip() if not pd.isna(url_val) else "No Link Available"
        
        # Format the simple text message
        # Added the company name next to the title just to make it clearer for you!
        message = f"[**{title} at {company}**]({url}), {location}\nMatch Score: {score}% "
        
        # Send via the 'content' argument instead of 'embeds'
        send_to_discord(content=message)
        
    print("Discord notification sent successfully!")

if __name__ == "__main__":
    main()