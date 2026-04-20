from jobspy import scrape_jobs
import pathlib
import time
import random

search_terms = ["graduate finance", "data","analyst","fintech"]
proxy_list = ["localhost"]
output_dir = pathlib.Path("output")
output_dir.mkdir(exist_ok=True)
# Define titles you want to exclude (case-insensitive)
exclude_terms = ['director', 'vp', 'vice president', 'head', 'principal', 'snr', 'lead','senior']

for term in search_terms:
    pause_time = random.uniform(30, 90)
    print(f"Human pause: waiting {pause_time}s...")
    time.sleep(pause_time)
    try:
        jobs = scrape_jobs(
            site_name=["linkedin"],
            search_term=term,
            location="Hong Kong",
            results_wanted=20,
            hours_old=72,
            proxies=proxy_list,
            user_agent ="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        )
        # print(jobs.head())
        # current_date = time.strftime("%Y-%m-%d")
        # file_path = output_dir / f"hk_{term}_{current_date}.csv"
        # jobs.to_csv(file_path, index=False)
        # print(f"Saved scraped jobs to {file_path}")
        
        if not jobs.empty:
            # --- FILTER OUT SENIOR ROLES ---
            # Creates a regex pattern like: \bdirector\b|\bvp\b|\bhead\b
            pattern = '|'.join([fr'\b{t}\b' for t in exclude_terms])
            
            original_count = len(jobs)
            jobs = jobs[~jobs['title'].str.contains(pattern, case=False, na=False)]
            print(f"Filtered out {original_count - len(jobs)} senior roles. Remaining: {len(jobs)}")
            
        if not jobs.empty:
            print(jobs.head())
            current_date = time.strftime("%Y-%m-%d")
            
            # Format the filename so spaces in terms become dashes (e.g. hk_graduate-finance_2026-04-20.csv)
            safe_term = term.replace(" ", "-")
            file_path = output_dir / f"hk_{safe_term}_{current_date}.csv"
            
            jobs.to_csv(file_path, index=False)
            print(f"Saved scraped jobs to {file_path}\n")
        else:
            print(f"No valid jobs left for '{term}' after filtering.\n")
    except Exception as e:
        print(f"An error occurred: {e}")
        break