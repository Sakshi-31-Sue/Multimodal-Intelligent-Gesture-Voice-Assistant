@echo off
cd /d "%~dp0"
py -3.10 -m venv .venv
if errorlevel 1 (
 echo Could not create Python 3.10 environment. Install Python 3.10 64-bit and retry.
 pause
 exit /b 1
)
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
if errorlevel 1 (echo Installation failed. Read the error above. & pause & exit /b 1)
if not exist .env copy .env.example .env
if not exist data mkdir data
if not exist models mkdir models
echo Installation complete. See README.md for the offline Vosk model setup.
pause
