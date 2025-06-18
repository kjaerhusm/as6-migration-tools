import os

def check_uad_files(root_dir):
    """
    Checks if .uad files are located in any directory ending with Connectivity/OpcUA.
    Returns a list of misplaced .uad files.

    Args:
        root_dir (str): Root directory of the project.

    Returns:
        list: List of misplaced .uad file paths.
    """
    required_suffix = os.path.normpath(os.path.join("Connectivity", "OpcUA"))
    misplaced_files = []

    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".uad"):
                current_dir = os.path.normpath(root)  # Normalize the directory path
                # Check if the directory ends with the required suffix
                if not current_dir.endswith(required_suffix):
                    misplaced_files.append(os.path.join(root, file))

    return misplaced_files