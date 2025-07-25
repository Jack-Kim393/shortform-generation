@echo off
REM Change to the directory where this script is located
cd /d "%~dp0"

REM Activate the virtual environment and run the streamlit app
call venv\Scripts\activate.bat
streamlit run app.py

REM Keep the window open after execution (optional)
pause
