# flow_2_enrich.py
import pandas as pd
import pathlib
import time
import random
import glob

# Import JobSpy's internal LinkedIn scraper and models
from jobspy.linkedin import LinkedIn
from jobspy.model import ScraperInput, Site, DescriptionFormat

output_dir = pathlib.Path("output")

def enrich_linkedin_descriptions(csv_path):
    print(f"\nProcessing {csv_path}...")
    df = pd.read_csv(csv_path)
    
    # Check if the dataframe has jobs and a description column
    if df.empty or 'id' not in df.columns:
        print("Empty or invalid CSV. Skipping.")
        return
        
    # We need to create a dummy ScraperInput because the internal _get_job_details 
    # method checks this to know if you want Markdown, HTML, or Plain text.
    dummy_input = ScraperInput(
        site_type=[Site.LINKEDIN],
        description_format=DescriptionFormat.MARKDOWN
    )
    
    # Instantiate the internal LinkedIn scraper
    # Note: Pass your proxies and user_agent here if you are using them
    li_scraper = LinkedIn(
        proxies=["localhost"], 
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    li_scraper.scraper_input = dummy_input 

    updated_count = 0

    for index, row in df.iterrows():
        # Only fetch if it's a LinkedIn job and the description is missing
        if row['site'] == 'linkedin' and pd.isna(row.get('description')):
            
            # JobSpy prefixes LinkedIn IDs with "li-" (e.g., "li-3693012711")
            # We must strip it to get the raw numeric ID for the URL request
            raw_job_id = str(row['id']).replace('li-', '')
            
            try:
                # Use JobSpy's exact internal method to fetch and parse the page
                job_details = li_scraper._get_job_details(raw_job_id)
                
                # Update the dataframe with the parsed description
                if job_details and job_details.get('description'):
                    df.at[index, 'description'] = job_details['description']
                    updated_count += 1
                    print(f"  [{index+1}/{len(df)}] Fetched description for: {row['title']}")
                else:
                    print(f"  [{index+1}/{len(df)}] No description found for: {row['title']}")
                    
            except Exception as e:
                print(f"  [{index+1}/{len(df)}] Error fetching job {raw_job_id}: {e}")
            
            # The crucial human-like pause between EVERY individual description fetch
            pause_time = random.uniform(3.5, 8.2)
            time.sleep(pause_time)
            
    # Save the enriched data back to the same CSV (or a new one)
    if updated_count > 0:
        df.to_csv(csv_path, index=False)
        print(f"Saved {updated_count} new descriptions to {csv_path}")
    else:
        print("No new descriptions were fetched.")

# Loop through all CSVs in the output directory
csv_files = glob.glob(f"{output_dir}/*.csv")
for file in csv_files:
    print(f"\n--- Starting enrichment for {file} ---")
    enrich_linkedin_descriptions(file)