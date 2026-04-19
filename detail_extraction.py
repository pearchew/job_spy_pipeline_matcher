import pandas as pd
from pathlib import Path
import ollama
from datetime import datetime

output_dir = Path("output")
output_dir.mkdir(exist_ok=True)
files_to_process = []
latest_date = None
master_log_path = Path("output") / "master_log.csv"
today_str = datetime.now().strftime("%Y-%m-%d")
if not master_log_path.exists():
    master_log_path.write_text(
        "processed_date,keyword,company,title,date_posted,extracted_skills,job_url,description\n"
    )  # Create with headers

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


def extract_skills(description):
    extraction_prompt = f"""
  You are an AI text extraction engine specializing in technical recruitment.
Your task is to analyze the following job description and extract the top 5 mandatory technical skills required for the role.

CRITICAL INSTRUCTIONS:
1. Ignore company bios, benefits, and "What we offer" sections. 
2. Focus your attention specifically on sections outlining candidate expectations. Look for headers or phrases such as:
   - Requirements / Minimum Qualifications
   - What we look for / What you'll need
   - About You / Your Profile
   - Skills and Experience
3. Return ONLY a comma-separated list of the 5 most critical technical skills. Absolutely no introductory text or markdown formatting.
4. If the text is empty or you cannot find clear technical requirements, return exactly: n/a

Job Description:
{description}
  """
    extraction_response = ollama.chat(
        model="llama3.2", messages=[{"role": "user", "content": extraction_prompt}]
    )
    extracted_skills = extraction_response["message"]["content"]
    print("\n--- AI Extracted Skills ---")
    print(extracted_skills)
    return extracted_skills.strip()


for file_details in files_to_process:
    file_path = file_details["path"]
    if file_path.exists():
        df = pd.read_csv(file_path)
    else:
        print("File not found! Double check your filename.")
    df["keyword"] = file_details["keyword"]
    df["extracted_skills"] = df["description"].apply(extract_skills)
    df["processed_date"] = today_str
    df[
        [
            "processed_date",
            "keyword",
            "company",
            "title",
            "date_posted",
            "extracted_skills",
            "job_url",
            "description",
        ]
    ].to_csv(
        master_log_path, mode="a", index=False, header=not master_log_path.exists()
    )
