@echo off

REM Checking if python is availabl
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python is not installed. Install Python and try again.
    exit /b
)

REM Checking the version of python
for /f "delims=" %%i in ('python -c "import sys; print('.'.join(map(str, sys.version_info[:3])))"') do set PYVERSION=%%i
echo Found a version of Python: %PYVERSION%

REM Creating a virtual environment
python -m venv venv

REM Checking the success of virtual environment creation
if not exist "venv" (
    echo Failed to create a virtual environment. Make sure you have the venv module for Python installed.
    exit /b
)

REM Activating the virtual environment
call venv\Scripts\activate

REM Updating pip and installing requirements
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Download model YOLOv8n
powershell -Command "Invoke-WebRequest -Uri https://github.com/ultralytics/assets/releases/download/v8.1.0/yolov8n.pt -OutFile yolov8n.pt"

echo The virtual environment is configured and dependencies are installed. The YOLOv8n model is loaded.
