# Job Spy AI Pipeline Matcher

## 🎯 Project Goal
The goal of this project is to automate the tedious process of job hunting by building an intelligent, end-to-end pipeline. It automatically scrapes relevant job postings, fetches full job descriptions, and uses local Large Language Models (LLMs) to cross-reference each job against your resume. Finally, it provides a clean, interactive dashboard to review your top-matching jobs, highlighting your matched skills and identifying exact skill gaps for every role.

## 🧠 What It Does (Project Outline)
This project is orchestrated by `main.py` and is broken down into four primary modules:

1. **Data Ingestion (Base Runs)**
   * `job_spy_linked_in_base_run.py`: Uses `jobspy` to scrape LinkedIn for recent job postings based on search terms and locations defined in `config.json`. It automatically filters out senior-level roles.
   * `google_sheets_base_run.py`: Pulls manually tracked jobs from a published Google Sheet, maps the columns to the JobSpy schema, and filters for today's entries.
2. **Data Enrichment**
   * `job_spy_linked_in_enrichment_run.py`: Scans the newly fetched jobs and uses JobSpy's internal LinkedIn scraper to scrape the full markdown job descriptions for any postings that are missing them.
3. **AI Evaluation & Screening**
   * `gap_and_opp_screen.py`: Feeds your `resume.md` and the enriched job descriptions into a local LLM via Ollama. It prompts the AI to extract candidate expectations, calculate a match score (0-100%), and output matched skills and skill gaps in JSON format. Deduplicates and saves the results to a master tracker.
4. **Visualization & Review**
   * `comparison_dashboard.py`: A Streamlit web application that provides two views:
     * **Job Board View:** Sorts jobs by their AI match score, displaying company info, matched skills, skill gaps, and a side-panel for reading the full job description.
     * **Model Comparison:** Allows you to compare the evaluation results of two different LLM models side-by-side to see which model evaluates job fit better.

---

## ⚙️ Setup Instructions

### Prerequisites
* **Python 3.8+** installed on your machine.
* **Ollama** installed and running locally (required for the AI evaluation step).

### 1. Environment Setup
Clone the repository and set up a Python virtual environment to keep dependencies isolated.

**For Mac/Linux:**