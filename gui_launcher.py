import os
import sys
import subprocess
import threading
import importlib.util
import tkinter as tk
from tkinter import filedialog, ttk
from tkinter import messagebox

class MigrationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AS4 to AS6 Migration Tool")
        self.root.geometry("1500x700")

        self.selected_folder = tk.StringVar()
        self.selected_script = tk.StringVar(value='Evaluate AS4 project')
        self.last_line_was_status = False

        base_dir = os.path.dirname(os.path.abspath(__file__))

        self.scripts = {
            'Evaluate AS4 project': os.path.join(base_dir, '', 'as4_to_as6_analyzer.py'),
            'AsMathToAsBrMath': os.path.join(base_dir, 'helpers', 'asmath_to_asbrmath.py'),
            'AsStringToAsBrStr': os.path.join(base_dir, 'helpers', 'asstring_to_asbrstr.py'),
            'OpcUa Update': os.path.join(base_dir, 'helpers', 'asopcua_update.py')
        }

        self.build_ui()

    def build_ui(self):
        frame = ttk.Frame(self.root, padding=10)
        frame.pack(fill='x')

        ttk.Label(frame, text="Project folder:").pack(anchor='w')
        folder_entry = ttk.Entry(frame, textvariable=self.selected_folder, width=80)
        folder_entry.pack(side='left', fill='x', expand=True)
        ttk.Button(frame, text="Browse", command=self.browse_folder).pack(side='left', padx=5)

        script_frame = ttk.Frame(self.root, padding=10)
        script_frame.pack(fill='x')
        ttk.Label(script_frame, text="Select script:").pack(side='left', anchor='w')
        script_menu_frame = ttk.Frame(script_frame, borderwidth=2, relief="groove")
        script_menu_frame.pack(side='left', padx=5, pady=5)
        script_menu = ttk.OptionMenu(script_menu_frame, self.selected_script, self.selected_script.get(), *self.scripts.keys())
        script_menu.pack(anchor='w')
        script_menu.config(width=20)  # Set fixed width to approximately 100px
        run_button = ttk.Button(script_frame, text="Run", command=self.run_script)
        run_button.pack(side='left', padx=5)
        run_button.config(state='disabled')
        self.selected_folder.trace_add('write', lambda *args: run_button.config(state='normal' if self.selected_folder.get() else 'disabled'))
        save_log_button = ttk.Button(script_frame, text="Save Log As...", command=self.save_log)
        save_log_button.pack(side='left', padx=5)
        save_log_button.config(state='disabled')
        self.script_ran = tk.BooleanVar(value=False)
        self.script_ran.trace_add('write', lambda *args: save_log_button.config(state='normal' if self.script_ran.get() else 'disabled'))

        self.status_label = ttk.Label(self.root, text="", font=("Courier", 12), background="black", foreground="yellow", anchor="w")
        self.status_label.pack(fill='x', padx=10)

        self.log_text = tk.Text(self.root, wrap='word', height=25, bg='black', fg='lime')
        self.log_text.pack(fill='both', expand=True, padx=10, pady=10)
        self.log_text.config(state='disabled')

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.selected_folder.set(folder)

    def run_script(self):
        self.log_text.config(state='normal')
        self.log_text.delete('1.0', tk.END)
        self.log_text.config(state='disabled')
        self.status_label.config(text="")
        self.last_line_was_status = False
        thread = threading.Thread(target=self.execute_script, daemon=True)
        thread.start()

    def execute_script(self):
        folder = self.selected_folder.get()
        script = self.scripts.get(self.selected_script.get())

        if not os.path.exists(folder) or not os.path.exists(script):
            self.append_log("Error: Invalid folder or script path.")
            return

        env = os.environ.copy()
        env['PYTHONUNBUFFERED'] = '1'
        env['PYTHONIOENCODING'] = 'utf-8'

        process = subprocess.Popen(
            [sys.executable, script, folder],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
            env=env
        )

        for line in process.stdout:
            stripped = line.strip()
            if "Processing file" in line:
                self.status_label.config(text=stripped)
                self.last_line_was_status = True
            elif stripped == "" and self.last_line_was_status:
                self.last_line_was_status = False  # skip the empty line after status
            else:
                self.status_label.config(text="")
                self.append_log(line)
                self.last_line_was_status = False

        process.wait()
        self.status_label.config(text="--- Script Finished ---")
        self.script_ran.set(True)

    def append_log(self, message):
        self.log_text.config(state='normal')
        try:
            self.log_text.insert(tk.END, message)
        except UnicodeEncodeError:
            self.log_text.insert(tk.END, message.encode('utf-8', errors='replace').decode('utf-8'))
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')


    def save_log(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                log_content = self.log_text.get("1.0", tk.END)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(log_content)
                messagebox.showinfo("Success", f"Log saved to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file:\n{e}")


if __name__ == '__main__':
    root = tk.Tk()
    app = MigrationGUI(root)
    root.mainloop()