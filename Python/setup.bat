@echo off
setlocal
cd /d "%~dp0"

echo Setting up Python Docker Model in "%CD%"...
if not exist "%~dp0.venv\Scripts\python.exe" (
    where py >nul 2>&1
    if not errorlevel 1 (
        py -3 -m venv "%~dp0.venv"
    ) else (
        python -m venv "%~dp0.venv"
    )
    if errorlevel 1 (
        echo Could not create the virtual environment.
        exit /b 1
    )
)

"%~dp0.venv\Scripts\python.exe" -m pip install -r "%~dp0requirements.txt"
if errorlevel 1 (
    echo Setup failed.
    exit /b 1
)
echo Setup complete. Run run.bat to start the app.
exit /b 0
