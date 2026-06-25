# Batch PDF Printer

Small Windows desktop app to select multiple PDFs, reorder them, choose a printer, and print them all silently via [SumatraPDF](https://www.sumatrapdfreader.org/).

## Prerequisites

1. **Python 3.10+**
2. **SumatraPDF** — installed automatically by `setup.bat` via winget, or manually from https://www.sumatrapdfreader.org/download-free-pdf-viewer

SumatraPDF is a Windows app, not a Python package. It cannot go into the venv; winget installs it system-wide:

```bat
winget install SumatraPDF.SumatraPDF --accept-package-agreements --accept-source-agreements
```

## First-time setup

```bat
setup.bat
```

This creates `.venv`, installs Python dependencies, and installs SumatraPDF.

## Run from source

```bat
run.bat
```

Or manually:

```bat
.\.venv\Scripts\python.exe main.py
```

## Build a standalone .exe

```bat
build.bat
```

Output: `dist\BatchPdfPrinter.exe`

## Usage

1. Click **Add PDFs...** and select one or more files.
2. Reorder with **Move Up** / **Move Down** if needed.
3. Pick a printer (defaults to your Windows default printer).
4. Click **Print All**.
5. If any files fail, use **Retry Failed**.

Settings (last printer and SumatraPDF path) are saved in `%APPDATA%\BatchPdfPrinter\config.json`.

## How it prints

The app calls SumatraPDF once per file:

```text
SumatraPDF.exe -print-to "Your Printer" -silent "file.pdf"
```

This avoids opening a viewer window for each PDF.
