# Utilities to call in multiple files
from pathlib import Path

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
