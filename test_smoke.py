"""Smoke tests for batch-pdf-printer core modules."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from core.config import DEFAULT_CONFIG, load_config, save_config
from core.print_engine import (
    PrintResult,
    describe_exit_code,
    find_sumatra,
    print_batch,
    print_pdf,
)
from core.printers import get_default_printer, list_printers


class ConfigTests(unittest.TestCase):
    def test_save_and_load_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config_dir = Path(tmp)
            config_file = config_dir / "config.json"
            with patch("core.config.CONFIG_DIR", config_dir), patch(
                "core.config.CONFIG_FILE", config_file
            ):
                save_config({"last_printer": "Test Printer", "sumatra_path": "C:\\x.exe"})
                loaded = load_config()
                self.assertEqual(loaded["last_printer"], "Test Printer")
                self.assertEqual(loaded["sumatra_path"], "C:\\x.exe")

    def test_load_missing_returns_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config_dir = Path(tmp)
            config_file = config_dir / "missing.json"
            with patch("core.config.CONFIG_DIR", config_dir), patch(
                "core.config.CONFIG_FILE", config_file
            ):
                self.assertEqual(load_config(), DEFAULT_CONFIG)


class PrintEngineTests(unittest.TestCase):
    def test_describe_exit_code(self) -> None:
        self.assertIn("open file", describe_exit_code(1))
        self.assertEqual(describe_exit_code(99), "unknown error")

    def test_find_sumatra_custom_path(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".exe", delete=False) as tmp:
            path = Path(tmp.name)
        try:
            self.assertEqual(find_sumatra(str(path)), path)
        finally:
            path.unlink(missing_ok=True)

    @patch("core.print_engine.subprocess.run")
    def test_print_pdf_success(self, mock_run) -> None:
        mock_run.return_value.returncode = 0
        with tempfile.NamedTemporaryFile(suffix=".exe", delete=False) as tmp:
            exe = Path(tmp.name)
        try:
            result = print_pdf(exe, "Printer", "doc.pdf")
            self.assertTrue(result.success)
            self.assertEqual(result.message, "printed")
        finally:
            exe.unlink(missing_ok=True)

    @patch("core.print_engine.subprocess.run")
    def test_print_batch_reports_progress(self, mock_run) -> None:
        mock_run.return_value.returncode = 0
        with tempfile.NamedTemporaryFile(suffix=".exe", delete=False) as tmp:
            exe = Path(tmp.name)
        try:
            progress: list[tuple[int, int, PrintResult]] = []

            def on_progress(current: int, total: int, result: PrintResult) -> None:
                progress.append((current, total, result))

            with patch("core.print_engine.time.sleep"):
                results = print_batch(
                    exe,
                    "Printer",
                    ["a.pdf", "b.pdf"],
                    on_progress=on_progress,
                )
            self.assertEqual(len(results), 2)
            self.assertEqual(len(progress), 2)
            self.assertEqual(progress[-1][0], 2)
        finally:
            exe.unlink(missing_ok=True)


class PrinterTests(unittest.TestCase):
    def test_list_printers_returns_list(self) -> None:
        printers = list_printers()
        self.assertIsInstance(printers, list)

    def test_get_default_printer(self) -> None:
        default = get_default_printer()
        if default is not None:
            self.assertIsInstance(default, str)


if __name__ == "__main__":
    unittest.main()
