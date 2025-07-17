# Utilities to call in multiple files
import hashlib
import os
import sys
from pathlib import Path

from classes.ConsoleColors import ConsoleColors

_is_verbose = False

def get_build_number():
    try:
        version_file = Path(__file__).resolve().parent.parent / "version.txt"
        return version_file.read_text(encoding="utf-8").strip()
    except Exception:
        return "?"


def set_verbose(verbose):
    global _is_verbose
    _is_verbose = verbose


def log(message, log_file=None):
    print(message)  # Print to console
    if log_file:
        log_file.write(message + "\n")  # Write to file
        log_file.flush()  # Ensure data is written immediately


def log_v(message, log_file=None, prepend=""):
    if _is_verbose:
        log(f"{prepend}[VERBOSE] {message}", log_file)


def get_and_check_project_file(project_path):
    if not os.path.exists(project_path):
        if sys.stdin.isatty():
            print(ConsoleColors.ERROR)
        print(f"Error: The provided project path does not exist: '{project_path}'"
              "\nEnsure the path is correct and the project folder exists."
              "\nIf the path contains spaces, make sure to wrap it in quotes, like this:"
              f"\n   python {os.path.basename(sys.argv[0])} \"C:\\path\\to\\your\\project\"",
              file=sys.stderr)
        if sys.stdin.isatty():
            print(f"{ConsoleColors.RESET}\n")
        sys.exit(1)

    # Check if .apj file exists in the provided path
    apj_files = [file for file in os.listdir(project_path) if file.endswith(".apj")]
    if not apj_files:
        if sys.stdin.isatty():
            print(ConsoleColors.ERROR)
        print(f"Error: No .apj file found in the provided path: {project_path}"
              "\nPlease specify a valid Automation Studio project path.",
              file=sys.stderr)
        if sys.stdin.isatty():
            print(f"{ConsoleColors.RESET}\n")
        sys.exit(1)

    return apj_files[0]


def calculate_file_hash(file_path):
    """
    Calculates the hash (MD5) of a file for comparison purposes.
    """
    md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        while chunk := f.read(4096):
            md5.update(chunk)
    return md5.hexdigest()


def ask_user(message, default="y", parent=None, extra_note=""):
    """
    Ask the user a yes/no question. Uses terminal input if no GUI context.
    """
    if parent is not None:
        from utils.utils import ask_user_gui
        cleaned_msg = (
            message.replace("(y/n)", "")
            .replace("[y]", "")
            .replace("[n]", "")
            .strip(": ")
            .strip()
        )
        result = ask_user_gui(cleaned_msg, parent, extra_note=extra_note)
        choice = "y" if result else "n"
        print(f"[INFO] {message} (User selected: '{choice}')")
        return choice

    # Fallback to terminal
    try:
        if sys.stdin and sys.stdin.isatty():
            return input(message).strip().lower()
    except Exception as e:
        print(f"[DEBUG] ask_user fallback triggered due to: {e}")
    print(f"[INFO] {message} (Automatically using default: '{default}')")
    return default


_icon_path = None
def set_gui_icon(path):
    global _icon_path
    _icon_path = path

def ask_user_gui(message: str, parent=None, extra_note: str = "") -> bool:
    """
    Display a Yes/No confirmation popup using customtkinter.
    If parent window is provided, center popup on it and use same icon.
    An optional extra_note can be provided for additional info.
    """
    import customtkinter as ctk
    import os

    if parent is None:
        root = ctk.CTk()
        root.withdraw()
    else:
        root = parent

    dialog = ctk.CTkToplevel(root)
    dialog.title("Confirmation")
    dialog.geometry("460x250")
    dialog.resizable(False, False)

    # Try using icon (only works some places with CTkToplevel)
    if _icon_path:
        try:
            dialog.iconbitmap(_icon_path)
        except Exception:
            pass

    if parent:
        parent.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - 230
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - 110
        dialog.geometry(f"+{x}+{y}")

    # Main container
    container = ctk.CTkFrame(dialog, fg_color="transparent")
    container.pack(padx=20, pady=(20, 10), fill="x")

    # Main message
    ctk.CTkLabel(
        container,
        text=message,
        font=("Segoe UI", 16, "bold"),
        wraplength=420,
        justify="center"
    ).pack(pady=(0, 20))

    # Recommendation
    ctk.CTkLabel(
        container,
        text="It is recommended to create a backup or use version control (e.g., Git) before continuing.",
        font=("Segoe UI", 13),
        wraplength=420,
        justify="center",
        text_color="#f59e0b"
    ).pack(pady=(0, 10))

    # Extra note if provided
    if extra_note:
        ctk.CTkLabel(
            container,
            text=extra_note,
            font=("Segoe UI", 13),
            wraplength=420,
            justify="center",
            text_color="gray"
        ).pack(pady=(0, 25))

    # Button row
    result = {"value": False}

    def on_yes():
        result["value"] = True
        dialog.destroy()

    def on_no():
        result["value"] = False
        dialog.destroy()

    dialog.protocol("WM_DELETE_WINDOW", on_no)
    dialog.bind("<Escape>", lambda e: on_no())

    button_frame = ctk.CTkFrame(container, fg_color="transparent")
    button_frame.pack(pady=(0, 5))
    ctk.CTkButton(button_frame, text="Yes", command=on_yes, width=100).pack(side="left", padx=15)
    ctk.CTkButton(button_frame, text="No", command=on_no, width=100).pack(side="left", padx=15)

    dialog.transient(parent)
    dialog.grab_set()
    dialog.lift()
    dialog.focus_force()
    root.wait_window(dialog)

    if parent is None:
        root.destroy()

    return result["value"]

