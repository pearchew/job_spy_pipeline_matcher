import pandas as pd
import glob
import os
import time

def clean_master_files(days_to_keep=14):
    output_dir = "output"
    tailored_dir = os.path.join(output_dir, "tailored_resumes")
    
    # Calculate the exact cutoff timestamp for file deletion
    # (Current time in seconds minus the number of seconds in `days_to_keep`)
    current_time = time.time()
    cutoff_timestamp = current_time - (days_to_keep * 24 * 60 * 60)
    
    # Calculate the cutoff date for pandas row filtering
    cutoff_date = pd.to_datetime('today') - pd.Timedelta(days=days_to_keep)
    
    print(f"🧹 Starting cleanup. Target: Data/Files older than {days_to_keep} days ({cutoff_date.strftime('%Y-%m-%d')})")

    # --- LOGIC 1: CLEAN UP ROWS IN THE MASTER CSV ---
    # This keeps your original logic: We don't delete the master file, 
    # we just open it and drop rows where the processed_date is older than 14 days.
    master_files = glob.glob(os.path.join(output_dir, "matched_master_*.csv"))
    for file in master_files:
        print(f"\n[1] Processing row-level cleanup for: {os.path.basename(file)}")
        try:
            df = pd.read_csv(file)
            if 'processed_date' in df.columns:
                original_len = len(df)
                
                # Convert processed_date to datetime objects for easy comparison
                df['processed_date_dt'] = pd.to_datetime(df['processed_date'], errors='coerce')
                
                # Filter to keep only jobs posted on or after the cutoff date (or where date parsing failed)
                df_filtered = df[(df['processed_date_dt'] >= cutoff_date) | (df['processed_date_dt'].isna())].copy()
                df_filtered = df_filtered.drop(columns=['processed_date_dt'])
                
                # Overwrite the cleaned data back to the same file
                df_filtered.to_csv(file, index=False)
                
                removed_count = original_len - len(df_filtered)
                print(f"  ✅ Removed {removed_count} old rows. {len(df_filtered)} jobs currently retained.")
            else:
                print(f"  ⚠️ Warning: 'processed_date' column not found. Skipping.")
        except Exception as e:
            print(f"  ❌ Error processing {file}: {e}")

    # --- LOGIC 2: DELETE DAILY SCRAPED CSVs ---
    # The pipeline generates multiple 'run_*.csv' files every day. 
    # This logic checks the file's last modified time and physically deletes it if it's too old.
    print(f"\n[2] Processing file-level cleanup for daily run CSVs...")
    run_files = glob.glob(os.path.join(output_dir, "run_*.csv"))
    deleted_runs = 0
    
    for file in run_files:
        # Get the time the file was last modified
        file_modified_time = os.path.getmtime(file)
        
        # If the file is older than the cutoff timestamp, delete it
        if file_modified_time < cutoff_timestamp:
            try:
                os.remove(file)
                deleted_runs += 1
            except Exception as e:
                print(f"  ❌ Failed to delete {os.path.basename(file)}: {e}")
                
    print(f"  ✅ Deleted {deleted_runs} old daily run CSV files.")

    # --- LOGIC 3: DELETE TAILORED RESUMES (.md) ---
    # The pipeline generates tailored markdown resumes in a subfolder. 
    # This logic checks their modified times and physically deletes them to prevent indefinite build-up.
    print(f"\n[3] Processing file-level cleanup for tailored markdown resumes...")
    deleted_resumes = 0
    
    if os.path.exists(tailored_dir):
        resume_files = glob.glob(os.path.join(tailored_dir, "*.md"))
        for file in resume_files:
            file_modified_time = os.path.getmtime(file)
            
            # If the resume is older than the cutoff timestamp, delete it
            if file_modified_time < cutoff_timestamp:
                try:
                    os.remove(file)
                    deleted_resumes += 1
                except Exception as e:
                    print(f"  ❌ Failed to delete {os.path.basename(file)}: {e}")
                    
        print(f"  ✅ Deleted {deleted_resumes} old tailored resume files.")
    else:
        print("  ℹ️ No tailored_resumes directory found. Skipping.")

    print("\n🎉 Master cleanup completed successfully!")

if __name__ == "__main__":
    clean_master_files(days_to_keep=14)