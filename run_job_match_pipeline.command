#!/bin/bash

# Navigate to the directory where this script is located
cd "$(dirname "$0")"

echo "Starting Job Spy Pipeline..."

# Activate the virtual environment
source venv/bin/activate

# Run the main pipeline script
python3 main.py

echo "Copying data to frontend..."
cp output/matched_master_*.csv front_end/src/data/

# Push the newly generated CSVs to GitHub
echo ""
echo "Pushing updates to GitHub..."
git add output/
git commit -m "Auto-update today's scraped jobs"
git push


echo "Pushing to discord..."
python3 discord_notifier.py

echo ""
echo "Done! Starting the frontend server..."

# Navigate to the frontend directory and start the server
cd front_end
npm run dev