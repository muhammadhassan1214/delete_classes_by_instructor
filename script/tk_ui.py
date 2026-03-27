import os
import sys
import threading
import io
import contextlib
import logging
import tkinter.messagebox as messagebox
import customtkinter as ctk
from typing import List

# Ensure imports resolve when running from repo root
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.append(CURRENT_DIR)

from utils.instructors import load_instructors
from main import main as run_automation

ACCENT = "#2563EB"
ACCENT_HOVER = "#1D4ED8"
SUCCESS = "#16A34A"
DANGER = "#DC2626"


class TkLogHandler(logging.Handler):
    """Forward std logging records into the UI log box."""

    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    def emit(self, record):
        try:
            msg = self.format(record)
            self.callback(msg)
        except Exception:
            self.handleError(record)


class ScrollableCombo(ctk.CTkFrame):
    """Custom dropdown with a scrollable list to avoid oversized menus."""

    def __init__(self, master, values: List[str], ids: List[str], height: int = 36, dropdown_height: int = 260, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.values = values
        self.ids = ids
        self.dropdown_height = dropdown_height
        self.var = ctk.StringVar(value=values[0] if values else "")

        self.entry = ctk.CTkEntry(self, textvariable=self.var, state="readonly", height=height)
        self.entry.grid(row=0, column=0, sticky="ew")

        self.btn = ctk.CTkButton(self, text="▾", width=32, height=height, command=self._toggle)
        self.btn.grid(row=0, column=1, padx=(6, 0))

        self.grid_columnconfigure(0, weight=1)
        self.dropdown = None

    def _toggle(self):
        if self.dropdown and self.dropdown.winfo_exists():
            self.dropdown.destroy()
            self.dropdown = None
        else:
            self._open_dropdown()

    def _open_dropdown(self):
        if not self.values:
            return
        # Create dropdown window
        self.dropdown = ctk.CTkToplevel(self)
        self.dropdown.overrideredirect(True)
        self.dropdown.attributes("-topmost", True)

        # Position just below the entry
        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height()
        self.dropdown.geometry(f"{self.winfo_width()}x{self.dropdown_height}+{x}+{y}")

        container = ctk.CTkScrollableFrame(self.dropdown, width=self.winfo_width(), height=self.dropdown_height)
        container.pack(fill="both", expand=True)

        for idx, label in enumerate(self.values):
            def on_select(i=idx):
                self.var.set(self.values[i])
                self.selected_id = self.ids[i]
                self._toggle()
            btn = ctk.CTkButton(container, text=label, anchor="w", height=32, command=on_select)
            btn.pack(fill="x", padx=4, pady=2)

        self.selected_id = self.ids[0] if self.ids else ""

    def update_values(self, values: List[str], ids: List[str]):
        self.values = values
        self.ids = ids
        if values:
            self.var.set(values[0])
        else:
            self.var.set("")
        if self.dropdown and self.dropdown.winfo_exists():
            self.dropdown.destroy()
            self.dropdown = None

    def get_label(self) -> str:
        return self.var.get()

    def get_selected_id(self) -> str:
        label = self.var.get()
        try:
            idx = self.values.index(label)
            return self.ids[idx]
        except ValueError:
            return self.ids[0] if self.ids else ""


class DeleteClassesApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Atlas – Delete Classes by Instructor")
        self.geometry("760x520")
        self.minsize(640, 420)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.instructors = load_instructors()
        if not self.instructors:
            messagebox.showerror("Instructors missing", "No instructors found in utils/instructors.csv")
            self.destroy()
            return

        self.combo_ids = [item["id"] for item in self.instructors]
        self.combo_labels = [f"{item['id']} / {item['name'] or item['label']}" for item in self.instructors]

        self.status_var = ctk.StringVar(value="Select an instructor and start.")
        self.search_var = ctk.StringVar()

        self._install_log_handler()

        self._build_header()
        self._build_search_row()
        self._build_combo_row()
        self._build_actions()
        self._build_log_area()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)

    def destroy(self):
        # Drop the log handler to avoid duplicate logs if the window is reopened.
        root_logger = logging.getLogger()
        if hasattr(self, "_log_handler") and self._log_handler in root_logger.handlers:
            root_logger.removeHandler(self._log_handler)
        super().destroy()

    # UI construction
    def _build_header(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=0, column=0, padx=18, pady=(16, 8), sticky="ew")
        frame.grid_columnconfigure(1, weight=1)

        title = ctk.CTkLabel(frame, text="🗑️Delete Classes", font=ctk.CTkFont(size=22, weight="bold"))
        title.grid(row=0, column=0, sticky="w")

        subtitle = ctk.CTkLabel(frame, text="Choose an instructor, then cancel their classes via Atlas API.", font=ctk.CTkFont(size=13), text_color="gray")
        subtitle.grid(row=1, column=0, sticky="w")

        self.mode_var = ctk.StringVar(value="🌙  Dark")
        mode_toggle = ctk.CTkSegmentedButton(frame, values=["☀️  Light", "🌙  Dark"], command=self._toggle_mode, font=ctk.CTkFont(size=13))
        mode_toggle.set("🌙  Dark")
        mode_toggle.grid(row=0, column=1, rowspan=2, sticky="e")

    def _build_search_row(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=1, column=0, padx=18, pady=4, sticky="ew")
        frame.grid_columnconfigure(1, weight=1)

        lbl = ctk.CTkLabel(frame, text="Search", font=ctk.CTkFont(size=14, weight="bold"))
        lbl.grid(row=0, column=0, sticky="w", padx=(0, 10))

        entry = ctk.CTkEntry(frame, textvariable=self.search_var, placeholder_text="Search by id or name", height=36)
        entry.grid(row=0, column=1, sticky="ew")
        self.search_var.trace_add("write", self._filter_instructors)

    def _build_combo_row(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=2, column=0, padx=18, pady=4, sticky="ew")
        frame.grid_columnconfigure(1, weight=1)

        lbl = ctk.CTkLabel(frame, text="Instructor", font=ctk.CTkFont(size=14, weight="bold"))
        lbl.grid(row=0, column=0, sticky="w", padx=(0, 10))

        self.combo = ScrollableCombo(
            frame,
            values=self.combo_labels,
            ids=self.combo_ids,
            height=36,
            dropdown_height=260,
        )
        self.combo.grid(row=0, column=1, sticky="ew")

    def _build_actions(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=3, column=0, padx=18, pady=10, sticky="ew")
        frame.grid_columnconfigure(0, weight=1)

        status = ctk.CTkLabel(frame, textvariable=self.status_var, wraplength=620)
        status.grid(row=0, column=0, sticky="w")

        self.start_btn = ctk.CTkButton(frame, text="🚀  Start deleting", fg_color=ACCENT, hover_color=ACCENT_HOVER, height=40, command=self._on_start)
        self.start_btn.grid(row=0, column=1, sticky="e", padx=(10, 0))

    def _build_log_area(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=4, column=0, padx=18, pady=(4, 18), sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        lbl = ctk.CTkLabel(frame, text="Log", font=ctk.CTkFont(size=14, weight="bold"))
        lbl.grid(row=0, column=0, sticky="w", pady=(0, 6))

        self.log_text = ctk.CTkTextbox(frame, wrap="word", font=ctk.CTkFont(family="Consolas", size=12))
        self.log_text.grid(row=1, column=0, sticky="nsew")
        self.log_text.configure(state="disabled")

    # Theme toggle
    def _toggle_mode(self, choice: str):
        if "Light" in choice:
            ctk.set_appearance_mode("light")
        else:
            ctk.set_appearance_mode("dark")

    # Search filtering
    def _filter_instructors(self, *_args):
        query = self.search_var.get().lower().strip()
        filtered_labels = []
        filtered_ids = []
        for item in self.instructors:
            label = f"{item['id']} / {item['name'] or item['label']}"
            if query in label.lower():
                filtered_labels.append(label)
                filtered_ids.append(item["id"])
        use_labels = filtered_labels or self.combo_labels
        use_ids = filtered_ids or self.combo_ids
        self.combo.update_values(use_labels, use_ids)

    # Logging helpers
    def _append_log(self, message: str):
        def write():
            self.log_text.configure(state="normal")
            self.log_text.insert("end", message + "\n")
            self.log_text.see("end")
            self.log_text.configure(state="disabled")
        self.after(0, write)

    def _install_log_handler(self):
        root_logger = logging.getLogger()
        for handler in root_logger.handlers:
            if isinstance(handler, TkLogHandler):
                self._log_handler = handler
                return
        handler = TkLogHandler(self._append_log)
        handler.setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        root_logger.addHandler(handler)
        self._log_handler = handler

    # Actions
    def _on_start(self):
        instructor_id = self.combo.get_selected_id()
        if not instructor_id:
            messagebox.showwarning("Missing selection", "Please choose an instructor.")
            return

        self.status_var.set(f"Starting automation for {instructor_id} (headless)...")
        self.start_btn.configure(state="disabled", text="⏳  Running...")
        self._append_log(f"--- Starting run for {instructor_id} ---")

        thread = threading.Thread(target=self._run_background, args=(instructor_id,), daemon=True)
        thread.start()

    def _run_background(self, instructor_id: str):
        buffer = io.StringIO()
        try:
            with contextlib.redirect_stdout(buffer):
                run_automation(instructor_id, headless=True)
            done_msg = f"Finished processing for instructor {instructor_id}."
        except Exception as exc:
            done_msg = f"Error while processing {instructor_id}: {exc}"
        captured = buffer.getvalue()
        self.after(0, lambda: self._finish_run(done_msg, captured))

    def _finish_run(self, message: str, captured: str):
        self.status_var.set(message)
        if captured:
            self._append_log(captured)
        self.start_btn.configure(state="normal", text="🚀  Start deleting")


def main():
    app = DeleteClassesApp()
    app.mainloop()


if __name__ == "__main__":
    main()

