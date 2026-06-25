import os
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

EXIT_CODE_MESSAGES = {
    1: "could not open file",
    2: "printer name typo or no default printer",
    3: "print cancelled",
    4: "could not create printer device context",
    5: "driver error — update printer driver",
    6: "SumatraPDF printing restricted by policy",
}


@dataclass
class PrintResult:
    path: str
    success: bool
    exit_code: int
    message: str


def default_sumatra_paths() -> list[Path]:
    local_app_data = Path(os.environ.get("LOCALAPPDATA", ""))
    return [
        Path(r"C:\Program Files\SumatraPDF\SumatraPDF.exe"),
        Path(r"C:\Program Files (x86)\SumatraPDF\SumatraPDF.exe"),
        local_app_data / "SumatraPDF" / "SumatraPDF.exe",
    ]


def find_sumatra(custom_path: str = "") -> Path | None:
    if custom_path:
        candidate = Path(custom_path)
        if candidate.is_file():
            return candidate
    for path in default_sumatra_paths():
        if path.is_file():
            return path
    return None


def describe_exit_code(code: int) -> str:
    if code in EXIT_CODE_MESSAGES:
        return EXIT_CODE_MESSAGES[code]
    return "unknown error"


def print_pdf(sumatra_exe: Path, printer: str, pdf_path: str) -> PrintResult:
    command = [
        str(sumatra_exe),
        "-print-to",
        printer,
        "-silent",
        pdf_path,
    ]
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        exit_code = completed.returncode
    except OSError as exc:
        return PrintResult(
            path=pdf_path,
            success=False,
            exit_code=-1,
            message=str(exc),
        )

    success = exit_code == 0
    if success:
        message = "printed"
    else:
        message = f"exit code {exit_code} — {describe_exit_code(exit_code)}"

    return PrintResult(path=pdf_path, success=success, exit_code=exit_code, message=message)


def print_batch(
    sumatra_exe: Path,
    printer: str,
    pdf_paths: list[str],
    *,
    delay_seconds: float = 0.4,
    on_progress=None,
) -> list[PrintResult]:
    results: list[PrintResult] = []
    total = len(pdf_paths)

    for index, pdf_path in enumerate(pdf_paths, start=1):
        result = print_pdf(sumatra_exe, printer, pdf_path)
        results.append(result)
        if on_progress:
            on_progress(index, total, result)
        if index < total:
            time.sleep(delay_seconds)

    return results
