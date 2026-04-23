import pandas as pd
from pathlib import Path
import ollama
from datetime import datetime
import json

with open("config.json", "r") as f:
    config = json.load(f)

# Use config values
selected_model = config.get("model", "gemma4:e2b")
resume_filename = config.get("resume_filename", "resume.md")
location = config.get("location", "Hong Kong")
location_safe = no_space_string = location.replace(" ", "")

output_dir = Path("output")
output_dir.mkdir(exist_ok=True)
files_to_process = []
latest_date = None
today_str = datetime.now().strftime("%Y-%m-%d")

resume_path = Path(resume_filename)
try:
    resume_content = resume_path.read_text(encoding="utf-8")
except FileNotFoundError:
    print(f"Error: Could not find the file at {resume_path.absolute()}")
    exit(1)

for file_path in output_dir.glob("run_*.csv"):
    parts = file_path.stem.split("_")
    try:
        # Assuming format: run_{keyword}_{location}_{date}
        keyword = parts[1]
        parsed_loc = parts[2] # Renamed so we don't overwrite the global 'location' variable
        date_str = parts[3]
        file_date = datetime.strptime(date_str, "%Y-%m-%d")

        files_to_process.append(
            {"path": file_path, "keyword": keyword, "location_tag": parsed_loc, "date": file_date}
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
    - Years of Experience Required
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
    print(
        f"Processing {len(files_to_process)} file(s) from the latest date: {latest_date.strftime('%Y-%m-%d')}"
    )

for file_details in files_to_process:
    file_path = file_details["path"]
    if file_path.exists():
        df = pd.read_csv(file_path)
        print(f"\nProcessing file: {file_path.name} with {len(df)} job descriptions...")
    else:
        print("File not found! Double check your filename.")
    df["evaluation_json"] = df["description"].apply(
        lambda desc: evaluate_fit(desc, resume_content, selected_model)
    )
    df["keyword"] = file_details["keyword"]
    df["processed_date"] = today_str
    
    file_loc_tag = file_details["location_tag"]
    
    # Check the location tag from the filename
    if file_loc_tag == "mixed":
        # Keep the original location from the CSV being looped through
        if "location" in df.columns:
            df["location"] = df["location"].fillna("N/A")
        else:
            df["location"] = "N/A"
            
    elif file_loc_tag == location_safe:
        # Output the location column as the location_safe match 
        # (Using `location` uses the original string from config with spaces, e.g., "Hong Kong")
        # (If you prefer it without spaces, you can change this to df["location"] = location_safe)
        df["location"] = location
        
    else:
        # Fallback just in case it's a completely different location
        df["location"] = file_loc_tag
    df["match_score"] = df["evaluation_json"].apply(lambda x: x.get("match_score", 0))
    df["matched_skills"] = df["evaluation_json"].apply(
        lambda x: ", ".join(x.get("matched_skills", []))
    )
    df["gaps_in_skill"] = df["evaluation_json"].apply(
        lambda x: ", ".join(x.get("gaps_in_skills", []))
    )
    safe_model_name = selected_model.replace(":", "_")
    matched_master_path = Path("output") / f"matched_master_{safe_model_name}.csv"
    if not matched_master_path.exists():
        matched_master_path.write_text(
            "processed_date,keyword,company,title,date_posted,match_score,matched_skills,gaps_in_skill,job_url,description,location\n"
        )  # Create with headers

    cols_to_save = [
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
    df_to_save = df[cols_to_save].copy()

    if matched_master_path.exists():
        # Load existing master data
        existing_df = pd.read_csv(matched_master_path)

        # Combine existing data with the newly processed data
        combined_df = pd.concat([existing_df, df_to_save], ignore_index=True)

        # Drop duplicates based on company, title, and job_url, keeping the most recent one
        combined_df = combined_df.drop_duplicates(
            subset=["company", "title", "job_url"], keep="last"
        )
    else:
        # If the file doesn't exist yet, just use the newly processed data
        combined_df = df_to_save.copy()

    # --- UNIQUE 5-DIGIT ID GENERATION (CLEAN-UP SAFE) ---
    # Ensure the 'job_id' column exists
    if 'job_id' not in combined_df.columns:
        combined_df['job_id'] = pd.NA

    missing_id_mask = combined_df['job_id'].isna()
    
    if missing_id_mask.any():
        # 1. Read the highest historical ID from a tracker file
        tracker_path = Path("output/last_job_id.txt")
        
        if tracker_path.exists():
            current_max = int(tracker_path.read_text().strip())
        else:
            # Fallback if tracker file doesn't exist yet: check CSV or start at 9999
            valid_ids = pd.to_numeric(combined_df['job_id'], errors='coerce').dropna()
            current_max = int(valid_ids.max()) if not valid_ids.empty else 9999
        
        # 2. Generate new sequential 5-digit IDs for the missing rows
        num_missing = missing_id_mask.sum()
        new_ids = range(current_max + 1, current_max + 1 + num_missing)
        
        # 3. Assign the new IDs
        combined_df.loc[missing_id_mask, 'job_id'] = new_ids
        
        # 4. Save the new highest ID to the tracker file so it's permanently remembered
        tracker_path.write_text(str(current_max + num_missing))

    # Convert job_id to integer to remove any trailing decimals
    combined_df['job_id'] = combined_df['job_id'].astype(int)

    # Overwrite the file with the clean, deduplicated data
    combined_df.to_csv(matched_master_path, index=False)
    
    print(f"Successfully saved {matched_master_path.name} (Total unique records: {len(combined_df)})")