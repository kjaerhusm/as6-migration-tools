import os
import re
import fnmatch

def check_files_for_compatibility(directory, file_patterns):
    """
    Checks the compatibility of .apj and .hw files within a directory.
    Validates that files have a minimum required version.

    Args:
        directory (str): Path to the directory to scan.
        file_patterns (list): Patterns of files to check, e.g., ['*.apj', '*.hw'].

    Returns:
        list: Results for incompatible files in the format (file_path, issue).
    """
    incompatible_files = []
    required_version_prefix = "4.12"

    for root, _, files in os.walk(directory):
        for file in files:
            if any(fnmatch.fnmatch(file, pattern) for pattern in file_patterns):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Extract version info from the file header
                    version_match = re.search(r'AutomationStudio Version="?([\d.]+)', content)
                    if version_match:
                        version = version_match.group(1)
                        if not version.startswith(required_version_prefix):
                            incompatible_files.append((file_path, f"Version {version}"))
                    else:
                        incompatible_files.append((file_path, "Version Unknown"))

                except Exception as e:
                    incompatible_files.append((file_path, f"Error reading file: {e}"))

    return incompatible_files
