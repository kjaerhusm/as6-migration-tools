import os
import sys
import threading
import importlib.util
import json
from pathlib import Path
import ttkbootstrap as ttk
from tkinter import filedialog, messagebox
from ttkbootstrap.constants import *

from utils import utils

SETTINGS_PATH = os.path.join(os.path.expanduser("~"), ".as6_migration_settings.json")

LABEL_FONT = ("Segoe UI", 14)
FIELD_FONT = ("Segoe UI", 13)
LOG_FONT = ("Consolas", 12)
SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

class RedirectText:
    def __init__(self, append_func, status_func):
        self.append_func = append_func
        self.status_func = status_func

    def write(self, string):
        if "\r" in string:
            self.status_func(string.strip())
        else:
            self.append_func(string)

    def flush(self):
        pass

class ModernMigrationGUI:
    def __init__(self):
        self.root = ttk.Window(themename="darkly")
        build = utils.get_build_number()
        self.root.title(f"AS4 to AS6 Migration Tool (Build {build})")
        self.root.geometry("1500x900")

        icon_path = os.path.join(getattr(sys, "_MEIPASS", os.path.abspath(".")), "gui_icon.ico")
        try:
            self.root.iconbitmap(icon_path)
        except Exception:
            pass

        self.selected_folder = ttk.StringVar()
        self.selected_script = ttk.StringVar(value="Evaluate AS4 project")
        self.verbose_mode = ttk.BooleanVar(value=False)
        self.script_ran = ttk.BooleanVar(value=False)
        self.spinner_running = False
        self.spinner_index = 0

        self.scripts = {
            "Evaluate AS4 project": self.resource_path("as4_to_as6_analyzer.py"),
            "AsMathToAsBrMath": self.resource_path("helpers/asmath_to_asbrmath.py"),
            "AsStringToAsBrStr": self.resource_path("helpers/asstring_to_asbrstr.py"),
            "OpcUa Update": self.resource_path("helpers/asopcua_update.py"),
            "Create mapp folders": self.resource_path("helpers/create_mapp_folders.py"),
        }

        self.load_last_folder()
        self.build_ui()
        self.selected_folder.trace_add("write", self.toggle_run_button)
        self.toggle_run_button()

    def resource_path(self, rel_path):
        base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
        return os.path.normpath(os.path.join(base, rel_path))

    def build_ui(self):
        self.build_header_ui()
        self.build_folder_ui()
        self.build_options_ui()
        self.build_status_ui()
        self.build_log_ui()
        self.build_save_ui()

    def build_header_ui(self):
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill="x", padx=20, pady=(10, 0))
        self.theme_button = ttk.Button(header_frame, text=self.get_theme_icon(), width=6, command=self.toggle_theme, bootstyle=INFO)
        self.theme_button.pack(side="right")

    def get_theme_icon(self):
        return "☀️" if self.root.style.theme.name.endswith("darkly") else "🌙"

    def toggle_theme(self):
        new_theme = "cosmo" if self.root.style.theme.name.endswith("darkly") else "darkly"
        self.root.style.theme_use(new_theme)
        self.theme_button.configure(text=self.get_theme_icon())
        self.save_settings()

    def build_folder_ui(self):
        folder_frame = ttk.Frame(self.root)
        folder_frame.pack(fill="x", padx=20, pady=5)
        folder_frame.columnconfigure(0, weight=1)

        ttk.Label(folder_frame, text="📂  Project folder:", font=LABEL_FONT).grid(row=0, column=0, sticky="w")
        folder_entry = ttk.Entry(folder_frame, textvariable=self.selected_folder, font=FIELD_FONT)
        folder_entry.grid(row=1, column=0, sticky="ew", padx=(0, 10), pady=(0, 5))
        self.browse_button = ttk.Button(folder_frame, text="📂 Browse", command=self.browse_folder, bootstyle=PRIMARY)
        self.browse_button.grid(row=1, column=1, pady=(0, 5))

    def build_options_ui(self):
        options_frame = ttk.Frame(self.root)
        options_frame.pack(fill="x", padx=20, pady=10)

        ttk.Label(options_frame, text="🧾  Select script:", font=LABEL_FONT).pack(side="left")
        ttk.Combobox(options_frame, textvariable=self.selected_script, values=list(self.scripts.keys()), width=40).pack(side="left", padx=10)
        ttk.Checkbutton(options_frame, text="Verbose Mode", variable=self.verbose_mode).pack(side="left", padx=10)
        self.run_button = ttk.Button(options_frame, text="🚀 Run", command=self.execute_script, state="disabled", bootstyle=SUCCESS)
        self.run_button.pack(side="left", padx=10)

    def build_status_ui(self):
        self.status_label = ttk.Label(self.root, text="", font=FIELD_FONT)
        self.status_label.pack(fill="x", padx=20, pady=(0, 5))

    def build_log_ui(self):
        self.log_text = ttk.Text(self.root, wrap="word", font=LOG_FONT)
        self.log_text.pack(fill="both", expand=True, padx=20, pady=10)
        self.log_text.configure(state="disabled")

    def build_save_ui(self):
        save_frame = ttk.Frame(self.root)
        save_frame.pack(fill="x", padx=20, pady=(0, 10))
        self.save_button = ttk.Button(save_frame, text="📥 Save Log", command=self.save_log, state="disabled", bootstyle=SECONDARY)
        self.save_button.pack(anchor="e")
        self.script_ran.trace_add("write", self.toggle_save_button)

    def toggle_run_button(self, *args):
        self.run_button.configure(state="normal" if self.selected_folder.get() else "disabled")

    def toggle_save_button(self, *args):
        self.save_button.configure(state="normal" if self.script_ran.get() else "disabled")

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.selected_folder.set(folder)
            self.save_settings()

    def load_last_folder(self):
        if os.path.exists(SETTINGS_PATH):
            try:
                with open(SETTINGS_PATH, "r") as f:
                    settings = json.load(f)
                last_folder = settings.get("last_folder")
                if last_folder and os.path.exists(last_folder):
                    self.selected_folder.set(last_folder)
            except Exception:
                pass

    def save_settings(self):
        settings = {"last_folder": self.selected_folder.get()}
        try:
            with open(SETTINGS_PATH, "w") as f:
                json.dump(settings, f)
        except Exception:
            pass

    def is_valid_as4_project(self, folder):
        required_dirs = ["Physical", "Logical"]
        has_apj_file = any(f.endswith(".apj") for f in os.listdir(folder))
        has_dirs = all(os.path.isdir(os.path.join(folder, d)) for d in required_dirs)
        return has_apj_file and has_dirs

    def execute_script(self):
        self.spinner_running = True
        self.spinner_index = 0
        self.animate_spinner()
        threading.Thread(target=self._worker_execute_script, daemon=True).start()

    def animate_spinner(self):
        if not self.spinner_running:
            return
        frame = SPINNER_FRAMES[self.spinner_index % len(SPINNER_FRAMES)]
        self.status_label.configure(text=f"{frame} Running")
        self.spinner_index += 1
        self.status_label.after(100, self.animate_spinner)

    def _worker_execute_script(self):
        self.clear_log()
        folder = self.selected_folder.get()
        script = self.scripts.get(self.selected_script.get())
        verbose = self.verbose_mode.get()

        if not os.path.exists(folder):
            self.append_log(f"[ERROR] Folder does not exist:\n{folder}")
            self.update_status("❌ Invalid folder")
            self.spinner_running = False
            return

        if not self.is_valid_as4_project(folder):
            self.append_log(f"[ERROR] Folder is not a valid AS4 project:\n{folder}")
            self.update_status("❌ Not a valid AS4 project")
            self.spinner_running = False
            return

        if not os.path.exists(script):
            self.append_log(f"[ERROR] Script not found:\n{script}")
            self.update_status("❌ Script missing")
            self.spinner_running = False
            return

        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            stdlib_path = Path(sys._MEIPASS) / "lib"
            if stdlib_path.exists():
                sys.path.insert(0, str(stdlib_path.resolve()))

        spec = importlib.util.spec_from_file_location("selected_script", script)
        module = importlib.util.module_from_spec(spec)
        sys.modules["selected_script"] = module

        original_stdout, original_stderr = sys.stdout, sys.stderr
        redirector = RedirectText(self.append_log, self.update_status)
        sys.stdout = redirector
        sys.stderr = redirector

        try:
            spec.loader.exec_module(module)
            sys.argv = ["analyzer", folder]
            if verbose:
                sys.argv.append("--verbose")
            module.main()
        except Exception as e:
            import traceback
            print(f"[ERROR] Execution failed: {e}")
            print(traceback.format_exc())
        finally:
            sys.stdout = original_stdout
            sys.stderr = original_stderr
            self.spinner_running = False

        self.update_status("✔ Script finished successfully")
        self.script_ran.set(True)

    def append_log(self, message):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", message)
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def update_status(self, message):
        self.status_label.after(0, lambda: self.status_label.configure(text=message))

    def save_log(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            try:
                log_content = self.log_text.get("1.0", "end")
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(log_content)
                messagebox.showinfo("Success", f"Log saved to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file:\n{e}")

    def clear_log(self):
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ModernMigrationGUI()
    app.run()