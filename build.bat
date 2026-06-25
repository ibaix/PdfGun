@echo off
setlocal

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Virtual environment not found. Run setup.bat first.
    exit /b 1
)

.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m PyInstaller --onefile --windowed --name BatchPdfPrinter main.py

echo.
echo Build complete: dist\BatchPdfPrinter.exe
endlocal
