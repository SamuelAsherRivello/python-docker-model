@echo off
setlocal
cd /d "%~dp0"

set "PYTHON_DOCKER_MODEL_ROOT=%~dp0"
set "STREAMLIT_LISTENER_PID="
for /f "usebackq delims=" %%P in (`powershell.exe -NoProfile -Command "$listener = Get-NetTCPConnection -LocalPort 8501 -State Listen -ErrorAction SilentlyContinue ^| Select-Object -First 1; if ($listener) { $listener.OwningProcess }"`) do set "STREAMLIT_LISTENER_PID=%%P"

if defined STREAMLIT_LISTENER_PID (
    echo Python Docker Model is already running at http://localhost:8501 ^(PID %STREAMLIT_LISTENER_PID%^).
    exit /b 0
)

if not exist "%~dp0.venv\Scripts\python.exe" (
    call "%~dp0setup.bat"
    if errorlevel 1 exit /b 1
)

if not exist "%~dp0.run" mkdir "%~dp0.run"

set "STREAMLIT_PID="
for /f "usebackq delims=" %%P in (`powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "$root = $env:PYTHON_DOCKER_MODEL_ROOT; $python = Join-Path $root '.venv\Scripts\python.exe'; $main = Join-Path $root 'main.py'; $stdout = Join-Path $root '.run\streamlit.stdout.log'; $stderr = Join-Path $root '.run\streamlit.stderr.log'; $process = Start-Process -FilePath $python -ArgumentList @('-m','streamlit','run',$main,'--server.port','8501','--server.headless','true') -WorkingDirectory $root -RedirectStandardOutput $stdout -RedirectStandardError $stderr -WindowStyle Hidden -PassThru; $process.Id"`) do set "STREAMLIT_PID=%%P"

if not defined STREAMLIT_PID (
    echo Could not start Streamlit. Check .run\streamlit.stderr.log for details.
    exit /b 1
)

echo Starting Python Docker Model at http://localhost:8501 ^(PID %STREAMLIT_PID%^).
echo Logs are written to "%~dp0.run".
exit /b 0
