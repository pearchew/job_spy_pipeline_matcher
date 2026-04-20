import pandas as pd
from pathlib import Path
import ollama
from datetime import datetime
import json

output_dir = Path("output")
output_dir.mkdir(exist_ok=True)
files_to_process = []
latest_date = None
today_str = datetime.now().strftime("%Y-%m-%d")

for file_path in output_dir.glob("hk_*.csv"):
    # filename example: hk_data-analyst_2026-04-19.csv
    # file_path.stem gives us 'hk_data-analyst_2026-04-19'
    parts = file_path.stem.split("_")
    try:
        # Assuming format: hk_{keyword}_{date}
        # keyword is the middle part, date is the last part
        keyword = parts[1]
        date_str = parts[2]
        file_date = datetime.strptime(date_str, "%Y-%m-%d")

        files_to_process.append(
            {"path": file_path, "keyword": keyword, "date": file_date}
        )
        # Track the latest date found in the folder
        if latest_date is None or file_date > latest_date:
            latest_date = file_date

    except (IndexError, ValueError):
        continue


def evaluate_fit(description, candidate_profile, model="gemma4:e2b"):
    if pd.isna(description) or not str(description).strip():
        print("Skipping empty description...")
        return {
            "match_score": 0,
            "matched_skills": [],
            "gaps_in_skills": [],
            "matched_domain_expertise": [],
            "gaps_in_domain_expertise": [],
        }
    print(f"\nEvaluating job description with model {model}...")
    extraction_prompt = f"""
    You are an AI job fit evaluation engine specializing in technical and finance recruitment.
    Your task is to cross-reference the job description and the candidate profile to extract skills and domain expertise, and calculate a match score.

    CRITICAL INSTRUCTIONS:
    1. Ignore company bios, benefits, and "What we offer" sections. 
    2. Focus your attention specifically on sections outlining candidate expectations. Look for headers or phrases such as:
    - Requirements / Minimum Qualifications
    - What we look for / What you'll need
    - About You / Your Profile
    - Skills and Experience
    - What you will do / Your role / Your responsibilities
    3. If the job description is empty or lacks clear requirements, return a score of 0 and empty lists.
    4. You must respond ONLY with a valid JSON object. Do not include markdown formatting like ```json.

    Return a JSON object with EXACTLY this structure:
    {{
        "match_score": <integer from 0 to 100 representing the percentage match>,
        "matched_skills": ["skill1", "skill2"],
        "gaps_in_skills": ["missing_skill1"],
        "matched_domain_expertise": ["sector1", "sector2"],
        "gaps_in_domain_expertise": ["missing_sector1"]
    }}

    Candidate Profile:
    {candidate_profile}

    Job Description:
    {description}
    """

    for attempt in range(3):  # Retry up to 3 times if JSON parsing fails
        try:
            print(f"Attempt {attempt + 1}...")
            evaluation_response = ollama.chat(
                model,
                messages=[{"role": "user", "content": extraction_prompt}],
                format="json",  # Ensure the response is treated as JSON
            )
            raw_response = evaluation_response["message"]["content"]
            analysis_dict = json.loads(raw_response)
            print(
                f"\n--- AI Evaluation Score: {analysis_dict.get('match_score', 0)}% ---"
            )
            return analysis_dict
        except json.JSONDecodeError:
            print(f"Warning: Invalid JSON on attempt {attempt + 1}. Retrying...")
    print(f"\n[ERROR] Model returned invalid JSON after 3 tries. Skipping row.")
    # Return a safe default so the script doesn't crash
    return {
        "match_score": 0,
        "matched_skills": [],
        "gaps_in_skills": [],
        "matched_domain_expertise": [],
        "gaps_in_domain_expertise": [],
    }

if latest_date:
    print(f"Latest file date found: {latest_date.strftime('%Y-%m-%d')}")
    files_to_process = [f for f in files_to_process if f["date"] == latest_date]
    print(f"Processing {len(files_to_process)} file(s) from the latest date: {latest_date.strftime('%Y-%m-%d')}")
resume_path = Path("output") / "resume.md"

try:
    resume_content = resume_path.read_text(encoding="utf-8")
except FileNotFoundError:
    print(f"Error: Could not find the file at {resume_path.absolute()}")
    exit(1)

for file_details in files_to_process:
    file_path = file_details["path"]
    if file_path.exists():
        df = pd.read_csv(file_path)
        print(f"\nProcessing file: {file_path.name} with {len(df)} job descriptions...")
    else:
        print("File not found! Double check your filename.")
    # model = "llama3.2"
    model = "phi4-mini"
    # model = "gemma4:e2b"
    df["evaluation_json"] = df["description"].apply(
        lambda desc: evaluate_fit(desc, resume_content, model)
    )
    df["keyword"] = file_details["keyword"]
    df["processed_date"] = today_str
    df["location"] = df["location"].fillna("N/A")
    df["match_score"] = df["evaluation_json"].apply(lambda x: x.get("match_score", 0))
    df["matched_skills"] = df["evaluation_json"].apply(
        lambda x: ", ".join(x.get("matched_skills", []))
    )
    df["gaps_in_skill"] = df["evaluation_json"].apply(
        lambda x: ", ".join(x.get("gaps_in_skills", []))
    )
    matched_master_path = Path("output") / f"matched_master_{model}.csv"
    if not matched_master_path.exists():
        matched_master_path.write_text(
            "processed_date,keyword,company,title,date_posted,match_score,matched_skills,gaps_in_skill,job_url,description,location\n"
        )  # Create with headers
    df[
        [
            "processed_date",
            "keyword",
            "company",
            "title",
            "date_posted",
            "match_score",
            "matched_skills",
            "gaps_in_skill",
            "job_url",
            "description",
            "location",
        ]
    ].to_csv(
        matched_master_path,
        mode="a",
        index=False,
        header=not matched_master_path.exists(),
    )
