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
