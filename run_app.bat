@echo off
REM ============================================
REM CS 425 Real Estate App - Run Script (Windows)
REM ============================================
REM This script starts the Flask development server.
REM Prerequisites:
REM   1. Python 3 is installed and added to PATH.
REM   2. Required packages are installed:
REM        pip install -r requirements.txt
REM
REM If you are using a conda environment, you can optionally
REM uncomment the 'call conda activate ...' line below and
REM change the environment name.

REM Change working directory to the folder where this script lives
cd /d "%~dp0"

REM OPTIONAL: activate a conda environment (uncomment and edit name)
call conda activate reape

REM Set Flask app and (optional) debug mode
set FLASK_APP=app.py
set FLASK_DEBUG=1

echo Starting Flask development server...
python -m flask run

echo.
echo If the browser does not open automatically, go to:
echo   http://127.0.0.1:5000/
echo.
pause
