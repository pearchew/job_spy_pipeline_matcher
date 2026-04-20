import subprocess
import time
import datetime

def run_script(script_name):
    print(f"========== RUNNING {script_name} ==========")
    script_start = time.time()
    
    # Run the script
    subprocess.run(["python", script_name], check=True)
    
    script_end = time.time()
    elapsed_seconds = script_end - script_start
    print(f"⏱️ [{script_name} finished in {elapsed_seconds:.2f} seconds]\n")

if __name__ == "__main__":
    print(f"🚀 Starting Job Match Pipeline at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    pipeline_start = time.time()
    
    try:
        # 1. Base Runs (Fetching jobs)
        run_script("job_spy_linked_in_base_run.py")
        run_script("google_sheets_base_run.py")
        
        # 2. Enrich missing descriptions
        run_script("job_spy_linked_in_enrichment_run.py")
        
        # 3. LLM Screening (Matching)
        run_script("gap_and_opp_screen.py")
        
        # Calculate total time
        pipeline_end = time.time()
        total_elapsed = pipeline_end - pipeline_start
        minutes = int(total_elapsed // 60)
        seconds = total_elapsed % 60
        
        print("==================================================")
        print(f"✅ Pipeline complete! Total execution time: {minutes} minutes and {seconds:.2f} seconds.")
        print("▶️ Run 'streamlit run comparison_dashboard.py' to view results.")
        print("==================================================")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Pipeline failed! Error occurred while running: {' '.join(e.cmd)}")