@echo off
echo Starting Job Spy Pipeline...

:: Activate the virtual environment
call venv\Scripts\activate.bat

:: Run the main pipeline script
python main.py

echo Copying data to frontend...
copy /Y output\matched_master_*.csv front_end\src\data\

:: Push the newly generated CSVs to GitHub
echo.
echo Pushing updates to GitHub...
git add output/
git commit -m "Auto-update today's scraped jobs"
git push

echo Pushing to Discord...
python discord_notifier.py

echo.
echo Done! Starting the frontend server...

:: Navigate to the frontend directory and open a new window to run the server
cd front_end
start npm run dev