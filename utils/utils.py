# Utilities to call in multiple files
from pathlib import Path


def get_build_number():
    try:
        version_file = Path(__file__).resolve().parent.parent / "version.txt"
        return version_file.read_text(encoding="utf-8").strip()
    except Exception:
        return "?"
