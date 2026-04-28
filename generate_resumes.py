import pandas as pd
from pathlib import Path
import ollama
from datetime import datetime
import json
import re

def generate_tailored_resumes():
    # 1. Load config and paths
    with open("config.json", "r") as f:
        config = json.load(f)

    eval_model = config.get("model", "gemma4:e4b")
    safe_model_name = eval_model.replace(":", "_")
    master_path = Path("output") / f"matched_master_{safe_model_name}.csv"
    
    resume_path = Path(config.get("resume_filename", "resume.md"))

    tailored_dir = Path("output") / "tailored_resumes"
    tailored_dir.mkdir(parents=True, exist_ok=True)

    if not resume_path.exists() or not master_path.exists():
        print(f"❌ Error: Missing base resume or master CSV.")
        return

    base_resume = resume_path.read_text(encoding="utf-8")
    df = pd.read_csv(master_path)

    # 2. Filter for today's high-match jobs
    today_str = datetime.now().strftime("%Y-%m-%d")
    df['match_score'] = pd.to_numeric(df['match_score'], errors='coerce').fillna(0)
    high_match_jobs = df[(df['processed_date'] == today_str) & (df['match_score'] >= 90)]

    if high_match_jobs.empty:
        print("ℹ️ No jobs processed today met the >90% match threshold. Skipping.")
        return

    print(f"🎯 Found {len(high_match_jobs)} job(s) >=90%. Generating MD resumes...")

    # 3. Generate Resumes
    for index, row in high_match_jobs.iterrows():
        company = str(row['company'])
        title = str(row['title'])
        job_id = row.get('job_id', 'NO_ID')
        description = row['description']

        print(f"\n📝 Tailoring resume for {company} - {title}...")

        # --- THE ANTI-HALLUCINATION PROMPT ---
        prompt = f"""
        You are an expert technical recruiter and resume writer. 
        I am providing you with my base resume and a job description. 

        CRITICAL INSTRUCTIONS:
        1. STRICT ANTI-HALLUCINATION RULE: You are strictly forbidden from inventing experience or swapping technologies. If the job description requires "Power BI" but my resume only lists "Tableau", you MUST keep "Tableau". Do not change the names of tools, platforms, or languages I have used just to match the ATS.
        2. SELECTIVE INCLUSION: Evaluate each bullet point against the job description. If a bullet point or an entire project has zero relevance to the target role, REMOVE IT entirely to save space. 
        3. F-PATTERN FORMATTING: Front-load surviving bullet points with a strong action verb and relevant, TRUE keywords from the job description. 
        4. STRICT TEMPLATE ADHERENCE: Output in the exact same Markdown layout as the Base Resume. Maintain the bold headers and right-aligned structure. Keep Company and Job Title headers intact even if you delete all bullet points under them to prevent employment gaps.

        Job Description:
        {description}

        Base Resume:
        {base_resume}
        """

        try:
            response = ollama.chat(
                model="qwen3:8b",
                messages=[{"role": "user", "content": prompt}]
            )
            
            tailored_md_content = response["message"]["content"]
            safe_filename = re.sub(r'[^\w\-_\. ]', '_', f"{job_id}_{company}_{title}.md")
            
            # Save ONLY the Markdown file
            md_file = tailored_dir / safe_filename
            md_file.write_text(tailored_md_content, encoding="utf-8")
            
            print(f"✅ Saved clean markdown to {md_file.name}")
            
        except Exception as e:
            print(f"❌ Failed to generate resume for {company}: {e}")

if __name__ == "__main__":
    generate_tailored_resumes()