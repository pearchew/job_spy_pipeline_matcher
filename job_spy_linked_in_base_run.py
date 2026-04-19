from jobspy import scrape_jobs
import pathlib
import time
import random

search_terms = ["graduate finance", "data","analyst","junior fintech"]
proxy_list = ["localhost"]
output_dir = pathlib.Path("output")
output_dir.mkdir(exist_ok=True)

for term in search_terms:
    pause_time = random.uniform(30, 90)
    time.sleep(pause_time)
    print(f"Human pause: waiting {pause_time}s...")
    try:
        jobs = scrape_jobs(
            site_name=["linkedin"],
            search_term=term,
            location="Hong Kong",
            results_wanted=20,
            hours_old=72,
            proxies=proxy_list,
            user_agent ="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            # linkedin_fetch_description=True 
        )
        print(jobs.head())
        current_date = time.strftime("%Y-%m-%d")
        file_path = output_dir / f"hk_{term}_{current_date}.csv"
        jobs.to_csv(file_path, index=False)
        print(f"Saved scraped jobs to {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")
        break