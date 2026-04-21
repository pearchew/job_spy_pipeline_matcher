import pandas as pd
import glob
import os

def clean_master_files(days_to_keep=14):
    output_dir = "output"
    
    # Find all matched_master CSV files in the output directory
    master_files = glob.glob(os.path.join(output_dir, "matched_master_*.csv"))
    
    if not master_files:
        print("No matched_master files found to clean.")
        return

    # Calculate the cutoff date (14 days ago)
    cutoff_date = pd.to_datetime('today') - pd.Timedelta(days=days_to_keep)
    print(f"Cleaning out jobs posted before: {cutoff_date.strftime('%Y-%m-%d')}")

    for file in master_files:
        print(f"\nProcessing {os.path.basename(file)}...")
        try:
            df = pd.read_csv(file)
            
            if 'processed_date' in df.columns:
                original_len = len(df)
                
                # Convert processed_date to datetime objects for easy comparison
                df['processed_date_dt'] = pd.to_datetime(df['processed_date'], errors='coerce')
                
                # Filter to keep only jobs posted on or after the cutoff date
                # We also keep rows where date parsing failed (NaT) just to be safe
                df_filtered = df[(df['processed_date_dt'] >= cutoff_date) | (df['processed_date_dt'].isna())].copy()
                
                # Drop the temporary datetime column
                df_filtered = df_filtered.drop(columns=['processed_date_dt'])
                
                # Save the cleaned data back to the same file
                df_filtered.to_csv(file, index=False)
                
                removed_count = original_len - len(df_filtered)
                print(f"✅ Removed {removed_count} old jobs. {len(df_filtered)} jobs currently retained.")
            else:
                print(f"⚠️ Warning: 'processed_date' column not found in {file}. Skipping.")
                
        except Exception as e:
            print(f"❌ Error processing {file}: {e}")

if __name__ == "__main__":
    clean_master_files(days_to_keep=14)