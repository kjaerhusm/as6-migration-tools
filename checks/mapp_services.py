import os
import re


def check_mapp_version(directory):
    """
    Checks for the mapp Services version in the .apj project file.

    Args:
        directory (str): Path to the project directory.

    Returns:
        list: List of warnings or information about mapp Services version.
    """
    messages = []
    apj_file = None

    for file in os.listdir(directory):
        if file.endswith(".apj"):
            apj_file = os.path.join(directory, file)
            break

    if not apj_file:
        return messages

    with open(apj_file, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            # Check for mapp Services version in the .apj file
            if ("<mapp " in line and "Version=" in line) or (
                "<mappServices" in line and "Version=" in line
            ):
                match = re.search(r'Version="(\d+)\.(\d+)', line)
                if match:
                    # Extract major and minor version numbers
                    major, minor = int(match.group(1)), int(match.group(2))
                    version_str = f"{major}.{minor}"
                    messages.append(f"Detected Mapp Services version: {version_str}")

                    if major == 5 and minor < 20:
                        messages.extend([
                            "It is recommended to use a mapp Services version 5.20 or later for the conversion.",
                            "If a mapp Services version older than 5.20 is used, the correct conversion of all configuration parameters is not guaranteed.",
                            "Please update the mapp Services version in AS4 to 5.20 or later before migrating to AS6."
                        ])
                    messages.extend([
                        "The automatic mapp Services configuration upgrade is only available with mapp Services 6.0.",
                        "Please ensure the project is converted using AS6 and mapp Services 6.0 before upgrading to newer mapp versions."
                    ])

            # Check for mappMotion version 5.x
            if "<mappMotion " in line and 'Version="5.' in line:
                messages.extend([
                    "Detected Mapp Motion version: 5.x",
                    "You must first upgrade mappMotion to version 6.0 using 'Change runtime versions' in AS6.",
                    "Once mappMotion 6.0 is set, a dialog will assist with converting all project configurations."
                ])

    # Make sure all mapp folders are present in the Physical directory
    # Get all folders in the Physical directory
    physical_path = os.path.join(directory, "Physical")
    if os.path.exists(physical_path) and os.path.isdir(physical_path):
        physical_folders = [
            f
            for f in os.listdir(physical_path)
            if os.path.isdir(os.path.join(physical_path, f))
        ]

        grouped_results = {}
        for folder in physical_folders:
            config_folder_path = os.path.join(physical_path, folder)

            # Check if mappServices folder exists in the config folder directory
            if os.path.exists(config_folder_path):
                # Check for sub folders in the config folder
                subfolders = [
                    f
                    for f in os.listdir(config_folder_path)
                    if os.path.isdir(os.path.join(config_folder_path, f))
                ]

                mapp_folders_to_check = ["mappServices", "mappMotion", "mappView"]
                found_mapp_folders = {folder: False for folder in mapp_folders_to_check}

                if subfolders:
                    # Walk through all directories
                    for root, dirs, files in os.walk(
                        os.path.join(config_folder_path, subfolders[0])
                    ):
                        for mapp_folder in mapp_folders_to_check:
                            if mapp_folder in dirs:
                                found_mapp_folders[mapp_folder] = True

                    for mapp_folder, found in found_mapp_folders.items():
                        if not found:
                            grouped_results.setdefault(folder, set()).add(mapp_folder)

        if grouped_results:
            result = "Some configurations are missing one or more of the mapp folders"
            for config_name, missing_mapp_folders in grouped_results.items():
                missing_folders = ", ".join(sorted(missing_mapp_folders))
                result += f"\n  - '{config_name}': {missing_folders}"
            result += "\nYou can use the script 'helpers/create_mapp_folders.py' to create the mapp folder structure in the Physical directory."
            messages.append(result)

    return messages
