import csv
from jobspy import scrape_jobs

jobs = scrape_jobs(
    site_name=["linkedin"],
    search_term="graduate",
    location="Hong Kong",
    results_wanted=20,
    hours_old=168,
)

print(jobs.head())