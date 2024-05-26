@echo off

where python >nul 2>nul
if %errorlevel% neq 0 (
    exit /b
)

for /f "delims=" %%i in ('python -c "import sys; print('.'.join(map(str, sys.version_info[:3])))"') do set PYVERSION=%%i

python -m venv venv

if not exist "venv" (
    exit /b
)

call venv\Scripts\activate

python -m pip install --upgrade pip
pip install -r requirements.txt

powershell -Command "Invoke-WebRequest -Uri https://github.com/ultralytics/assets/releases/download/v8.1.0/yolov8n.pt -OutFile yolov8n.pt"
