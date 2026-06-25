import threading
import tkinter as tk
import webbrowser
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from core.config import load_config, save_config
from core.print_engine import PrintResult, find_sumatra, print_batch
from core.printers import get_default_printer, list_printers
from ui.theme import (
    BG,
    MAGENTA,
    ORANGE,
    WHITE,
    apply_theme,
    draw_horizontal_gradient,
    style_listbox,
    style_log_text,
)

SUMATRA_DOWNLOAD_URL = "https://www.sumatrapdfreader.org/download-free-pdf-viewer"
HEADER_HEIGHT = 72


class BatchPdfPrinterApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Batch PDF Printer")
        self.geometry("580x700")
        self.minsize(540, 620)
        self.configure(bg=BG)

        self.config_data = load_config()
        self.pdf_paths: list[str] = []
        self.failed_paths: list[str] = []
        self.printing = False

        apply_theme(self)
        self._build_ui()
        self._load_printers()
        self._check_sumatra()
        self._update_print_state()

    def _build_ui(self) -> None:
        self._build_header()

        main = ttk.Frame(self, padding=(16, 12, 16, 16))
        main.pack(fill=tk.BOTH, expand=True)

        files_frame = ttk.LabelFrame(main, text="  PDF files  ", style="Card.TLabelframe", padding=10)
        files_frame.pack(fill=tk.BOTH, expand=True)

        list_container = ttk.Frame(files_frame, style="Card.TFrame")
        list_container.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.file_listbox = tk.Listbox(
            list_container,
            selectmode=tk.SINGLE,
            yscrollcommand=scrollbar.set,
            height=9,
        )
        style_listbox(self.file_listbox)
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.file_listbox.yview)

        file_buttons = ttk.Frame(files_frame, style="Card.TFrame")
        file_buttons.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(
            file_buttons, text="Add PDFs...", style="Accent.TButton", command=self._add_pdfs
        ).pack(side=tk.LEFT)
        ttk.Button(file_buttons, text="Move Up", command=self._move_up).pack(
            side=tk.LEFT, padx=(8, 0)
        )
        ttk.Button(file_buttons, text="Move Down", command=self._move_down).pack(
            side=tk.LEFT, padx=(8, 0)
        )
        ttk.Button(file_buttons, text="Remove", command=self._remove_selected).pack(
            side=tk.LEFT, padx=(8, 0)
        )
        ttk.Button(file_buttons, text="Clear", command=self._clear_files).pack(
            side=tk.LEFT, padx=(8, 0)
        )

        printer_frame = ttk.LabelFrame(main, text="  Printer  ", style="Card.TLabelframe", padding=10)
        printer_frame.pack(fill=tk.X, pady=(12, 0))

        self.printer_var = tk.StringVar()
        self.printer_combo = ttk.Combobox(
            printer_frame,
            textvariable=self.printer_var,
            state="readonly",
        )
        self.printer_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(printer_frame, text="Refresh", command=self._load_printers).pack(
            side=tk.LEFT, padx=(8, 0)
        )

        sumatra_frame = ttk.LabelFrame(
            main, text="  SumatraPDF  ", style="Card.TLabelframe", padding=10
        )
        sumatra_frame.pack(fill=tk.X, pady=(12, 0))

        self.sumatra_var = tk.StringVar(value=self.config_data.get("sumatra_path", ""))
        self.sumatra_entry = ttk.Entry(sumatra_frame, textvariable=self.sumatra_var)
        self.sumatra_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(sumatra_frame, text="Browse...", command=self._browse_sumatra).pack(
            side=tk.LEFT, padx=(8, 0)
        )

        action_frame = ttk.Frame(main)
        action_frame.pack(fill=tk.X, pady=(14, 0))

        self.print_button = ttk.Button(
            action_frame, text="Print All", style="Primary.TButton", command=self._start_print
        )
        self.print_button.pack(side=tk.LEFT)

        self.retry_button = ttk.Button(
            action_frame,
            text="Retry Failed",
            command=self._retry_failed,
            state=tk.DISABLED,
        )
        self.retry_button.pack(side=tk.LEFT, padx=(10, 0))

        progress_frame = ttk.LabelFrame(
            main, text="  Progress  ", style="Card.TLabelframe", padding=10
        )
        progress_frame.pack(fill=tk.BOTH, expand=True, pady=(12, 0))

        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            progress_frame, variable=self.progress_var, maximum=100
        )
        self.progress_bar.pack(fill=tk.X)

        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(progress_frame, textvariable=self.status_var, style="Card.TLabel").pack(
            anchor=tk.W, pady=(8, 0)
        )

        log_container = ttk.Frame(progress_frame, style="Card.TFrame")
        log_container.pack(fill=tk.BOTH, expand=True, pady=(8, 0))

        log_scroll = ttk.Scrollbar(log_container)
        log_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.log_text = tk.Text(
            log_container,
            height=7,
            wrap=tk.WORD,
            state=tk.DISABLED,
            yscrollcommand=log_scroll.set,
        )
        style_log_text(self.log_text)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scroll.config(command=self.log_text.yview)

    def _build_header(self) -> None:
        self.header_canvas = tk.Canvas(
            self,
            height=HEADER_HEIGHT,
            highlightthickness=0,
            bd=0,
            relief="flat",
        )
        self.header_canvas.pack(fill=tk.X)

        def redraw(_event=None) -> None:
            width = max(self.header_canvas.winfo_width(), 1)
            draw_horizontal_gradient(self.header_canvas, width, HEADER_HEIGHT, ORANGE, MAGENTA)
            self.header_canvas.delete("header-text")
            center_x = width // 2
            self.header_canvas.create_text(
                center_x,
                28,
                text="Batch PDF Printer",
                fill=WHITE,
                font=("Segoe UI", 17, "bold"),
                tags="header-text",
            )
            self.header_canvas.create_text(
                center_x,
                52,
                text="Select, reorder, and print multiple PDFs at once",
                fill=WHITE,
                font=("Segoe UI", 9),
                tags="header-text",
            )
            self.header_canvas.tag_raise("header-text")

        self.header_canvas.bind("<Configure>", redraw)
        self.after(50, redraw)

    def _check_sumatra(self) -> None:
        sumatra = find_sumatra(self.sumatra_var.get().strip())
        if sumatra:
            self.sumatra_var.set(str(sumatra))
            return

        if messagebox.askyesno(
            "SumatraPDF not found",
            "SumatraPDF is required for silent batch printing.\n\n"
            "Open the download page now?",
        ):
            webbrowser.open(SUMATRA_DOWNLOAD_URL)

    def _load_printers(self) -> None:
        printers = list_printers()
        self.printer_combo["values"] = printers

        preferred = self.config_data.get("last_printer") or get_default_printer() or ""
        if preferred in printers:
            self.printer_var.set(preferred)
        elif printers:
            self.printer_var.set(printers[0])
        else:
            self.printer_var.set("")

        self._update_print_state()

    def _browse_sumatra(self) -> None:
        path = filedialog.askopenfilename(
            title="Select SumatraPDF.exe",
            filetypes=[("SumatraPDF", "SumatraPDF.exe"), ("Executables", "*.exe")],
        )
        if path:
            self.sumatra_var.set(path)
            self._persist_config()

    def _add_pdfs(self) -> None:
        paths = filedialog.askopenfilenames(
            title="Select PDF files",
            filetypes=[("PDF files", "*.pdf")],
        )
        if not paths:
            return

        existing = set(self.pdf_paths)
        for path in paths:
            if path not in existing:
                self.pdf_paths.append(path)
                existing.add(path)
                self.file_listbox.insert(tk.END, Path(path).name)

        self._update_print_state()

    def _selected_index(self) -> int | None:
        selection = self.file_listbox.curselection()
        if not selection:
            return None
        return int(selection[0])

    def _move_up(self) -> None:
        index = self._selected_index()
        if index is None or index == 0:
            return
        self.pdf_paths[index - 1], self.pdf_paths[index] = (
            self.pdf_paths[index],
            self.pdf_paths[index - 1],
        )
        self._refresh_listbox(select_index=index - 1)

    def _move_down(self) -> None:
        index = self._selected_index()
        if index is None or index >= len(self.pdf_paths) - 1:
            return
        self.pdf_paths[index + 1], self.pdf_paths[index] = (
            self.pdf_paths[index],
            self.pdf_paths[index + 1],
        )
        self._refresh_listbox(select_index=index + 1)

    def _remove_selected(self) -> None:
        index = self._selected_index()
        if index is None:
            return
        del self.pdf_paths[index]
        self._refresh_listbox()

    def _clear_files(self) -> None:
        self.pdf_paths.clear()
        self._refresh_listbox()
        self.failed_paths.clear()
        self.retry_button.config(state=tk.DISABLED)

    def _refresh_listbox(self, select_index: int | None = None) -> None:
        self.file_listbox.delete(0, tk.END)
        for path in self.pdf_paths:
            self.file_listbox.insert(tk.END, Path(path).name)
        if select_index is not None and 0 <= select_index < len(self.pdf_paths):
            self.file_listbox.selection_set(select_index)
            self.file_listbox.see(select_index)
        self._update_print_state()

    def _update_print_state(self) -> None:
        can_print = bool(self.pdf_paths) and bool(self.printer_var.get()) and not self.printing
        self.print_button.config(state=tk.NORMAL if can_print else tk.DISABLED)

    def _persist_config(self) -> None:
        self.config_data["last_printer"] = self.printer_var.get()
        self.config_data["sumatra_path"] = self.sumatra_var.get().strip()
        save_config(self.config_data)

    def _append_log(self, line: str, *, success: bool) -> None:
        self.log_text.config(state=tk.NORMAL)
        tag = "ok" if success else "fail"
        self.log_text.insert(tk.END, line + "\n", tag)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def _start_print(self) -> None:
        if self.printing:
            return

        sumatra = find_sumatra(self.sumatra_var.get().strip())
        if not sumatra:
            messagebox.showerror(
                "SumatraPDF not found",
                "Set the path to SumatraPDF.exe before printing.",
            )
            return

        printer = self.printer_var.get().strip()
        if not printer:
            messagebox.showerror("No printer", "Select a printer before printing.")
            return

        self._persist_config()
        self._run_print(self.pdf_paths.copy())

    def _retry_failed(self) -> None:
        if self.printing or not self.failed_paths:
            return
        self._run_print(self.failed_paths.copy())

    def _run_print(self, paths: list[str]) -> None:
        sumatra = find_sumatra(self.sumatra_var.get().strip())
        if not sumatra:
            return

        self.printing = True
        self.failed_paths.clear()
        self.retry_button.config(state=tk.DISABLED)
        self.progress_var.set(0)
        self.status_var.set("Printing...")
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.config(state=tk.DISABLED)
        self._update_print_state()

        printer = self.printer_var.get().strip()

        def worker() -> None:
            results = print_batch(
                sumatra,
                printer,
                paths,
                on_progress=lambda current, total, result: self.after(
                    0, lambda: self._on_progress(current, total, result)
                ),
            )
            self.after(0, lambda: self._on_print_finished(results))

        threading.Thread(target=worker, daemon=True).start()

    def _on_progress(self, current: int, total: int, result: PrintResult) -> None:
        self.progress_var.set((current / total) * 100)
        name = Path(result.path).name
        if result.success:
            self._append_log(f"✓  {name}", success=True)
        else:
            self._append_log(f"✗  {name}  ({result.message})", success=False)
        self.status_var.set(f"Printing {current} of {total}...")

    def _on_print_finished(self, results: list[PrintResult]) -> None:
        self.printing = False
        success_count = sum(1 for result in results if result.success)
        failure_count = len(results) - success_count
        self.failed_paths = [result.path for result in results if not result.success]

        self.progress_var.set(100 if results else 0)
        self.status_var.set(
            f"Printed {success_count}/{len(results)}."
            + (f" {failure_count} failed." if failure_count else "")
        )

        if self.failed_paths:
            self.retry_button.config(state=tk.NORMAL)

        self._update_print_state()

        if failure_count:
            messagebox.showwarning(
                "Print finished with errors",
                f"Printed {success_count}/{len(results)}. {failure_count} failed.",
            )
        elif results:
            messagebox.showinfo(
                "Print finished",
                f"Successfully printed {success_count} file(s).",
            )


def run() -> None:
    app = BatchPdfPrinterApp()
    app.mainloop()
