# Utilities to call in multiple files
import concurrent.futures
import hashlib
import os
import sys
from pathlib import Path

from CTkMessagebox import CTkMessagebox

_is_verbose = False


class ConsoleColors:
    RESET = "\x1b[0m"  # Reset all formatting
    MANDATORY = "\x1b[1;31m"  # Set style to bold, red foreground.
    WARNING = "\x1b[1;33m"  # Set style to bold, yellow foreground.
    INFO = "\x1b[92m"  # Set style to light green foreground.


def get_build_number():
    try:
        version_file = Path(__file__).resolve().parent.parent / "version.txt"
        return version_file.read_text(encoding="utf-8").strip()
    except Exception:
        return "?"


def set_verbose(verbose):
    global _is_verbose
    _is_verbose = verbose


def log(message, log_file=None, when="", severity=""):
    if when != "":
        message = f"[{when}] {message}"
    if severity != "":
        # Farbliche Hervorhebung je nach Severity-Level
        if severity.upper() == "MANDATORY" or severity.upper() == "ERROR":
            colored_severity = (
                f"{ConsoleColors.MANDATORY}[{severity}]{ConsoleColors.RESET}"
            )
        elif severity.upper() == "WARNING":
            colored_severity = (
                f"{ConsoleColors.WARNING}[{severity}]{ConsoleColors.RESET}"
            )
        elif severity.upper() == "INFO":
            colored_severity = f"{ConsoleColors.INFO}[{severity}]{ConsoleColors.RESET}"
        else:
            colored_severity = f"[{severity}]"

        # Für Konsole mit Farbe
        console_message = f"{colored_severity} {message}"
        # Für Datei ohne Farbe
        file_message = f"[{severity}] {message}"
    else:
        console_message = message
        file_message = message

    # Print to console with colors (with newline at start)
    print(
        f"\n{console_message}",
        file=(sys.stderr if severity.upper() == "ERROR" else sys.stdout),
    )
    if log_file:
        log_file.write(file_message + "\n")  # Write to file without colors
        log_file.flush()  # Ensure data is written immediately


def log_v(message, log_file=None, prepend="", when="", severity=""):
    if _is_verbose:
        log(f"{prepend}[VERBOSE] {message}", log_file, when, severity)


def get_and_check_project_file(project_path):
    project_path = Path(project_path)
    if not project_path.exists():
        log(
            f"The provided project path does not exist: '{project_path}'"
            "\nEnsure the path is correct and the project folder exists."
            "\nIf the path contains spaces, make sure to wrap it in quotes, like this:"
            f'\n   python {os.path.basename(sys.argv[0])} "C:\\path\\to\\your\\project"',
            severity="ERROR",
        )
        sys.exit(1)

    # Check if .apj file exists in the provided path
    apj_file = next(project_path.glob("*.apj"), None)
    if not apj_file:
        log(
            f"No .apj file found in the provided path: {project_path}"
            "\nPlease specify a valid Automation Studio project path.",
            severity="ERROR",
        )
        sys.exit(1)

    return os.path.basename(apj_file)


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
        cleaned_msg = (
            message.replace("(y/n)", "")
            .replace("[y]", "")
            .replace("[n]", "")
            .strip(": ")
            .strip()
        )
        result = ask_user_gui(cleaned_msg, extra_note=extra_note)
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


def ask_user_gui(message: str, extra_note: str = "") -> bool:
    """
    Display a Yes/No confirmation popup using customtkinter.
    An optional extra_note can be provided for additional info.
    """
    final_message = f"{extra_note}\n\n" if extra_note else ""
    final_message += message
    msg = CTkMessagebox(
        title="Question",
        message=final_message,
        icon="question",
        option_1="Yes",
        option_2="No",
        width=460,
        wraplength=390,
    )
    response = msg.get()
    return response == "Yes"


def scan_files_parallel(root_dir, extensions, process_function, *args):
    """
    Scans files in a directory tree in parallel for specific content.

    Args:
        root_dir (Path): The root directory to search in.
        extensions (list): File extensions to include.
        process_function (callable): The function to apply on each file.
        *args: Additional arguments to pass to the process_function.

    Returns:
        list: Aggregated results from all scanned files.
    """
    results = []

    file_paths = [
        str(path)
        for ext in extensions
        for path in root_dir.rglob(f"*{ext}")
        if path.is_file()
    ]

    total_files = len(file_paths)
    display_progress(f"Found {total_files} files to process...")

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(process_function, str(path), *args): path
            for path in file_paths
        }
        for i, future in enumerate(concurrent.futures.as_completed(futures), 1):
            display_progress(f"Processing file {i}/{total_files}...")
            results.extend(future.result())

    display_progress("Processing complete.".ljust(50))  # Clear line
    return results


def display_progress(message):
    """
    Displays a progress message on the same line in the terminal.
    In GUI mode, stdout may be None, so we fall back to printing.
    """
    try:
        sys.stdout.write("\r" + " " * 80)
        sys.stdout.write("\r" + message)
        sys.stdout.flush()
    except Exception:
        # Fallback: simple print if stdout is unavailable
        print(message)
