import pandas as pd
from pathlib import Path
import ollama
from datetime import datetime
import json
import re
import markdown
from weasyprint import HTML, CSS

def generate_tailored_resumes():
    # 1. Load config
    with open("config.json", "r") as f:
        config = json.load(f)

    eval_model = config.get("model", "gemma4:e4b")
    safe_model_name = eval_model.replace(":", "_")
    master_path = Path("output") / f"matched_master_{safe_model_name}.csv"
    
    resume_filename = config.get("resume_filename", "resume.md")
    resume_path = Path(resume_filename)

    tailored_dir = Path("output") / "tailored_resumes"
    tailored_dir.mkdir(parents=True, exist_ok=True)

    if not resume_path.exists() or not master_path.exists():
        print(f"❌ Error: Missing base resume or master CSV.")
        return

    base_resume = resume_path.read_text(encoding="utf-8")
    df = pd.read_csv(master_path)

    today_str = datetime.now().strftime("%Y-%m-%d")
    df['match_score'] = pd.to_numeric(df['match_score'], errors='coerce').fillna(0)
    
    high_match_jobs = df[(df['processed_date'] == today_str) & (df['match_score'] > 90)]

    if high_match_jobs.empty:
        print("ℹ️ No jobs processed today met the >90% match threshold. Skipping.")
        return

    print(f"🎯 Generating tailored resumes with qwen3:8b...")

    # --- CSS for the F-Pattern PDF ---
    # Enforces strong left-alignment, bold starting text, and clean margins
    f_pattern_css = CSS(string='''
        @page { size: A4; margin: 0.75in; }
        body { font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; text-align: left; line-height: 1.3; font-size: 11pt; color: #000; }
        h1 { font-size: 18pt; text-align: left; margin-bottom: 2px; }
        h2 { font-size: 13pt; text-align: left; margin-top: 15px; margin-bottom: 5px; border-bottom: 1px solid #000; }
        p { margin: 0 0 5px 0; }
        ul { padding-left: 18px; margin-top: 2px; margin-bottom: 10px; }
        li { margin-bottom: 4px; text-align: left; }
        /* Optional: Make the first few words of bullets stand out slightly for scanning */
        li > strong:first-child { color: #222; }
    ''')

    for index, row in high_match_jobs.iterrows():
        company = str(row['company'])
        title = str(row['title'])
        job_id = row.get('job_id', 'NO_ID')
        description = row['description']

        print(f"\n📝 Tailoring resume for {company} - {title} (ID: {job_id})...")

        # --- The Prompt Enforcing the Template and F-Pattern ---
        prompt = f"""
        You are an expert technical recruiter and resume writer. 
        I am providing you with my base resume (formatted using the SheetsResume.com markdown standard) and a job description. 

        CRITICAL INSTRUCTIONS:
        1. SELECTIVE INCLUSION & ATS OPTIMIZATION: Do not feel obligated to use every bullet point from my base resume. Strictly evaluate each bullet point against the job description. If a bullet point or an entire technical project has zero relevance to the target role, REMOVE IT entirely to save space. Rewrite the surviving bullet points to naturally weave in keywords from the job description. Do not hallucinate fake experience.
        2. F-PATTERN FORMATTING: You MUST optimize for the "F-Pattern" reading style. Front-load every bullet point with a strong action verb and the most critical ATS keywords directly related to the job description. 
        3. STRICT TEMPLATE ADHERENCE: You must strictly output in the exact same Markdown layout as the Base Resume provided below. Maintain the bold headers and the right-aligned dates/locations. For older or highly irrelevant work experience, you may delete the bullet points entirely while keeping the Company and Job Title headers intact to prevent employment gaps.

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
            
            # Save safe filenames
            safe_filename_base = re.sub(r'[^\w\-_\. ]', '_', f"{job_id}_{company}_{title}")
            
            # 1. Save Markdown version
            md_file = tailored_dir / f"{safe_filename_base}.md"
            md_file.write_text(tailored_md_content, encoding="utf-8")
            
            # 2. Convert to PDF using Markdown -> HTML -> WeasyPrint
            html_content = markdown.markdown(tailored_md_content)
            pdf_file = tailored_dir / f"{safe_filename_base}.pdf"
            
            HTML(string=html_content).write_pdf(pdf_file, stylesheets=[f_pattern_css])
            
            print(f"✅ Saved MD and PDF to {tailored_dir}")
            
        except Exception as e:
            print(f"❌ Failed to generate resume for {company}: {e}")

if __name__ == "__main__":
    generate_tailored_resumes()