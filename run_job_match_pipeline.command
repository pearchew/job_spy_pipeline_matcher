#!/bin/bash

# Navigate to the directory where this script is located
cd "$(dirname "$0")"

echo "Starting Job Spy Pipeline..."

# Activate the virtual environment
source venv/bin/activate

# Run the main pipeline script
python3 main.py

# Push the newly generated CSVs to GitHub
echo ""
echo "Pushing updates to GitHub..."
git add output/
git commit -m "Auto-update today's scraped jobs"
git push

echo ""
echo "Done! Your Streamlit dashboard should update shortly."