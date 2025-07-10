import os
import re


def check_deprecated_string_functions(root_dir, extensions, deprecated_functions):
    """
    Scans all .st files in the project directory for deprecated string functions.

    Returns:
        list: A list of file paths where deprecated string functions were found.
    """
    deprecated_files = []

    for root, _, files in os.walk(root_dir):
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    if any(
                        re.search(rf"\b{func}\b", content)
                        for func in deprecated_functions
                    ):
                        deprecated_files.append(file_path)

    return deprecated_files


def check_deprecated_math_functions(root_dir, extensions, deprecated_functions):
    """
    Scans files for deprecated math function calls.

    Args:
        root_dir (str): The root directory to search in.
        extensions (list): List of file extensions to check.
        deprecated_functions (set): Set of deprecated math functions.

    Returns:
        list: A list of file paths where deprecated math functions were found.
    """
    deprecated_files = []
    # Match function names only when followed by '('
    function_pattern = re.compile(r"\b(" + "|".join(deprecated_functions) + r")\s*\(")

    for root, _, files in os.walk(root_dir):
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    if function_pattern.search(content):  # Only matches function calls
                        deprecated_files.append(file_path)

    return deprecated_files
