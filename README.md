
# 🕵️‍♂️ Job Spy Pipeline Matcher

An automated, end-to-end job scraping and AI-matching pipeline. This project fetches job listings from LinkedIn and custom Google Sheets, enriches the data, evaluates candidate fit using local LLMs (via Ollama), generates tailored markdown resumes for highly matched roles, and serves the results to a local React dashboard and a Discord channel.

## ✨ Features

* **Multi-Source Scraping:** Pulls daily job listings from LinkedIn (via JobSpy) and a custom Google Sheets tracker.
* **AI-Powered Screening:** Uses local LLMs (`gemma4:e4b`) to cross-reference job descriptions against your base resume, extracting skills, domain expertise, and calculating a precise `% Match Score`.
* **Automated Resume Tailoring:** Automatically drafts anti-hallucinated, highly targeted Markdown resumes (`qwen3:8b`) for any job with a match score of >= 90%.
* **Discord Integration:** Sends instant alerts to a Discord webhook with links to high-match jobs and attaches the auto-generated markdown resume directly to the chat.
* **Self-Cleaning Architecture:** Automatically purges daily scrape files, old tailored resumes, and database records older than 14 days to preserve disk space.
* **Interactive Frontend Dashboard:** A modern Vite/React frontend that visualizes the `matched_master` database for easy browsing, filtering, and comparison.
* **Cross-Platform Automation:** Includes `.bat` (Windows) and `.command` (Mac/Linux) scripts for 1-click execution, Git auto-syncing, and frontend server launching.

---

## 🛠️ Prerequisites

Before you begin, ensure you have the following installed on your system:
1. **[Python 3.8+](https://www.python.org/downloads/)**
2. **[Node.js & npm](https://nodejs.org/)** (For the frontend dashboard)
3. **[Ollama](https://ollama.com/)** (Running locally for AI evaluation)
4. **[Git](https://git-scm.com/)** ---

## 🚀 End-to-End Setup Guide

### 1. Clone the Repository
```bash
git clone [https://github.com/yourusername/job_spy_pipeline_matcher.git](https://github.com/yourusername/job_spy_pipeline_matcher.git)
cd job_spy_pipeline_matcher
```

### 2. Backend Setup (Python)
Create and activate a virtual environment, then install the dependencies:
```bash
# For Mac/Linux
python3 -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

### 3. Frontend Setup (React/Vite)
Navigate to the frontend directory and install the required node modules:
```bash
cd front_end
npm install
cd ..
```

### 4. Local AI (Ollama) Setup
Ensure the Ollama application is open and running in the background. You need to pull the specific models defined in your pipeline:
```bash
ollama pull gemma4:e4b
ollama pull qwen3:8b
```
*(Note: If you use different models in `config.json`, pull those instead).*

### 5. Configuration & Assets
1. **Base Resume:** Place your master resume in the root directory and name it `resume.md`. The AI will use this as the absolute source of truth to prevent hallucination.
2. **Pipeline Config:** Open `config.json` to define your search terms, target location, and job title exclusion keywords (e.g., "Director", "VP").
3. **Discord Webhook (Optional):** Open `discord_notifier.py` and replace the `WEBHOOK_URL` variable with your own Discord channel's webhook URL to receive notifications.

---

## ⚙️ Running the Pipeline

You can run the entire pipeline—from scraping to AI evaluation to launching the dashboard—with a single command. 

**For Mac/Linux:**
Open your terminal and run:
```bash
chmod +x run_job_match_pipeline.command
./run_job_match_pipeline.command
```

**For Windows:**
Simply double-click the `run_job_match_pipeline.bat` file, or run it via Command Prompt:
```cmd
run_job_match_pipeline.bat
```

### What happens when you run the script?
1. Activates the Python virtual environment.
2. Runs `main.py` which triggers scraping, AI screening, resume generation, cleanup, and Discord notifications.
3. Commits the newly generated data and tailored resumes to Git and pushes to your remote repository.
4. Starts the Vite development server for the frontend UI.

---

## 📂 Project Structure

```text
├── config.json                     # Search keywords, locations, model settings
├── main.py                         # Master orchestrator script
├── job_spy_linked_in_base_run.py   # Scrapes initial jobs from LinkedIn
├── google_sheets_base_run.py       # Pulls custom jobs from Google Sheets
├── job_spy_linked_in_enrichment.py # Fetches missing full job descriptions
├── gap_and_opp_screen.py           # Evaluates fit and scores jobs (Ollama)
├── generate_resumes.py             # Creates .md resumes for >90% matches
├── master_clean_up.py              # Prunes data/files older than 14 days
├── discord_notifier.py             # Sends high-match alerts to Discord
├── resume.md                       # YOUR base resume (Source of truth)
├── output/                         # Auto-generated CSVs and tailored resumes
├── front_end/                      # React/Vite Dashboard Application
├── run_job_match_pipeline.bat      # Windows execution wrapper
└── run_job_match_pipeline.command  # Mac/Linux execution wrapper
```

## ⚠️ Troubleshooting

* **Pipeline crashes instantly on screening:** Ensure the Ollama app is running on your machine before starting the pipeline. 
* **Zero jobs found:** LinkedIn may be rate-limiting your IP. JobSpy includes human-pauses, but consider adjusting the sleep intervals or using a proxy if you get completely blocked.
* **Frontend doesn't show new data:** Ensure the `.bat` or `.command` scripts are successfully pushing the `output` data to the `front_end/src/data` folder.
```
