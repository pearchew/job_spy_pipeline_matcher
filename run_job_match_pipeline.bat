@echo off
echo Starting Job Spy Pipeline...

:: Activate the virtual environment
call venv\Scripts\activate.bat

:: Run the main pipeline script
python main.py

:: Push the newly generated CSVs to GitHub
echo.
echo Pushing updates to GitHub...
git add output/
git commit -m "Auto-update today's scraped jobs"
git push

echo.
echo Done! Your Streamlit dashboard should update shortly.
pause