@echo off
:: Change directory to the location of this batch file
cd /d "%~dp0"

echo Starting Job Spy Pipeline...

:: Activate the virtual environment
call .venv\Scripts\activate.bat

:: Run the main pipeline script
python main.py

:: Push the newly generated CSVs (and frontend data) to GitHub
echo.
echo Pushing updates to GitHub...
git add output/ front_end/src/data/
git commit -m "Auto-update today's scraped jobs"
git push

echo.
echo Done!
echo Starting the frontend server...

:: Navigate to the frontend directory and open a new window to run the server
cd front_end
:: Using cmd /k keeps the terminal window open if npm crashes, letting you read the error
start cmd /k "npm run dev"