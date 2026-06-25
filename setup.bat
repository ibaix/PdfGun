@echo off
setlocal

cd /d "%~dp0"

echo Creating virtual environment...
python -m venv .venv
if errorlevel 1 exit /b 1

echo Installing Python dependencies...
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 exit /b 1

echo Installing SumatraPDF via winget...
winget install SumatraPDF.SumatraPDF --accept-package-agreements --accept-source-agreements
if errorlevel 1 (
    echo.
    echo winget install failed. Install SumatraPDF manually from:
    echo https://www.sumatrapdfreader.org/download-free-pdf-viewer
    exit /b 1
)

echo.
echo Setup complete.
echo Run the app with: run.bat
endlocal
