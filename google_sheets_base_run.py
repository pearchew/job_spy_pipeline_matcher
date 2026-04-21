import pandas as pd
import pathlib
import time
import re
import requests
import io
import urllib3
import json

# Suppress the insecure request warning that pops up when verify=False
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

with open('config.json', 'r') as f:
    config = json.load(f)
exclude_terms = config.get("exclude_terms", [])
master_filename = config.get("master_filename", "matched_master_gemma4_e2b.csv")

def extract_linkedin_id(url):
    """Extracts the numeric job ID from various LinkedIn URL formats."""
    if pd.isna(url):
        return None
    
    url_str = str(url)
    match = re.search(r'(?:view/|jobs/|currentJobId=)(\d+)', url_str)
    
    if match:
        return f"li-{match.group(1)}"
    return None

def run_google_sheet_import():
    print("Downloading data from Google Sheets...")
    
    # Your published CSV link
    sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTqlls80exZsDr7zWRioTuFygD-GVCnBYPBxKOhFVbXjSFF9La1o9APVnRSVtqPxqjJYIfjgwgA0iow/pub?gid=0&single=true&output=csv"
    
    try:
        response = requests.get(sheet_url, verify=False)
        response.raise_for_status() 
        df = pd.read_csv(io.StringIO(response.text))
    except Exception as e:
        print(f"Failed to download Google Sheet: {e}")
        return

    # --- 1. COLUMN MAPPING ---
    column_mapping = {
        'Job Title': 'title',
        'Company Name': 'company',
        'Company': 'company',
        'Job Link': 'job_url',
        'Link': 'job_url',
        'Location': 'location'
    }
    df.rename(columns=column_mapping, inplace=True)

    # --- 2. FORMAT THE DATE ---
    if 'Date' in df.columns:
        # Convert "20/04/2026 07:36:44" to "2026-04-20" format
        df['date_posted'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce').dt.strftime('%Y-%m-%d')

# --- 3. FILTER OUT JOBS ALREADY IN MASTER CSV ---
    current_date = time.strftime("%Y-%m-%d")
    master_path = pathlib.Path("output") / master_filename
    
    if master_path.exists():
        original_count = len(df)
        master_df = pd.read_csv(master_path)
        
        # 1. Get existing Job URLs
        existing_urls = set(master_df['job_url'].dropna().tolist())
        
        # 2. Get existing Company + Title combinations (as a fallback for missing/altered URLs)
        master_df['comp_title'] = master_df['company'].astype(str).str.lower().str.strip() + "_" + master_df['title'].astype(str).str.lower().str.strip()
        existing_comp_titles = set(master_df['comp_title'].dropna().tolist())
        
        # Create the same combination in our newly downloaded sheet
        if 'company' in df.columns and 'title' in df.columns:
            df['comp_title'] = df['company'].astype(str).str.lower().str.strip() + "_" + df['title'].astype(str).str.lower().str.strip()
        else:
            df['comp_title'] = ""
            
        # Filter: Keep rows where the URL is NOT in existing_urls AND the comp_title is NOT in existing_comp_titles
        df = df[~df['job_url'].isin(existing_urls) & ~df['comp_title'].isin(existing_comp_titles)]
        
        # Clean up the temporary column
        df = df.drop(columns=['comp_title'])
        
        print(f"Filtered {original_count} total jobs down to {len(df)} new jobs not present in {master_filename}.")
        
        if len(df) == 0:
            print("No new jobs found to process. Exiting without saving a new CSV.")
            return
    else:
        print(f"Master file '{master_filename}' not found. Processing all {len(df)} jobs from the sheet.")
    
    if 'title' in df.columns:
        pattern = '|'.join([fr'\b{t}\b' for t in exclude_terms])
        original_len_before_filter = len(df)
        df = df[~df['title'].str.contains(pattern, case=False, na=False)]
        print(f"Filtered out {original_len_before_filter - len(df)} senior roles based on title keywords.")
        
        if len(df) == 0:
            print("All of today's jobs were senior roles. Exiting.")
            return

    # --- 4. INJECT REQUIRED JOBSPY COLUMNS ---
    if 'job_url' not in df.columns:
        print("Error: Could not find a 'job_url' column.")
        return

    df['site'] = 'linkedin'
    df['id'] = df['job_url'].apply(extract_linkedin_id)

    # Drop rows where we couldn't parse a LinkedIn ID
    original_len = len(df)
    df = df.dropna(subset=['id'])
    if len(df) < original_len:
        print(f"Dropped {original_len - len(df)} rows that did not contain valid LinkedIn URLs.")

    # --- 5. ALIGN TO EXACT JOBSPY SCHEMA ---
    STANDARD_COLUMNS = [
        "id", "site", "job_url", "job_url_direct", "title", "company", "location", 
        "date_posted", "job_type", "salary_source", "interval", "min_amount", 
        "max_amount", "currency", "is_remote", "job_level", "job_function", 
        "listing_type", "emails", "description", "company_industry", "company_url", 
        "company_logo", "company_url_direct", "company_addresses", "company_num_employees", 
        "company_revenue", "company_description", "skills", "experience_range", 
        "company_rating", "company_reviews_count", "vacancy_count", "work_from_home_type"
    ]

    for col in STANDARD_COLUMNS:
        if col not in df.columns:
            df[col] = None

    df = df[STANDARD_COLUMNS]

    # --- 6. EXPORT TO OUTPUT FOLDER ---
    output_dir = pathlib.Path("output")
    output_dir.mkdir(exist_ok=True)

    file_path = output_dir / f"run_googlesheet_{current_date}.csv"
    
    df.to_csv(file_path, index=False)
    print(f"Success! Saved {len(df)} jobs from Google Sheets to {file_path}")

if __name__ == "__main__":
    run_google_sheet_import()