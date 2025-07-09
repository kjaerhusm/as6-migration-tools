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
            if ("<mapp " in line and "Version=" in line) or ("<mappServices" in line and "Version=" in line):
                match = re.search(r'Version="(\d+)\.(\d+)', line)
                if match:
                    # Extract major and minor version numbers
                    major = int(match.group(1))
                    minor = int(match.group(2))
                    version_str = f"{major}.{minor}"
                    messages.append(f"Detected Mapp Services version: {version_str}")
                    if major == 5 and minor < 20:
                        messages.append("It is recommended to use a mapp Services version 5.20 or later for the conversion.")
                        messages.append("If a mapp Services version older than 5.20 is used, the correct conversion of all configuration parameters is not guaranteed.")
                        messages.append("Please update the mapp Services version in AS4 to 5.20 or later before migrating to AS6.")
                    messages.append("The automatic mapp Services configuration upgrade is only available with mapp Services 6.0.")
                    messages.append("Please ensure the project is converted using AS6 and mapp Services 6.0 before upgrading to newer mapp versions.")

            # Check for mappMotion version 5.x
            if "<mappMotion " in line and 'Version="5.' in line:
                messages.append("Detected Mapp Motion version: 5.x")
                messages.append("You must first upgrade mappMotion to version 6.0 using 'Change runtime versions' in AS6.")
                messages.append("Once mappMotion 6.0 is set, a dialog will assist with converting all project configurations.")

    # Make sure all mapp folders are present in the Physical directory
    # Get all folders in the Physical directory
    physical_path = os.path.join(directory, "Physical")
    if os.path.exists(physical_path) and os.path.isdir(physical_path):
        physical_folders = [f for f in os.listdir(physical_path) 
                          if os.path.isdir(os.path.join(physical_path, f))]

        for folder in physical_folders:
            config_folder_path = os.path.join(physical_path, folder)
            
            # Check if mappServices folder exists in the config folder directory
            if os.path.exists(config_folder_path):     
                # Check for sub folders in the config folder
                subfolders = [f for f in os.listdir(config_folder_path) 
                            if os.path.isdir(os.path.join(config_folder_path, f))]
                
                if subfolders:
                    # Walk through all directories
                    mappServices_path = False
                    mappMotion_path = False
                    mappView_path = False
                    for root, dirs, files in os.walk(os.path.join(config_folder_path, subfolders[0])):
                        if "mappServices" in dirs:
                            mappServices_path = True
                        if "mappMotion" in dirs:
                            mappMotion_path = True
                        if "mappView" in dirs:
                            mappView_path = True

                    if not mappServices_path:
                        messages.append(f"No mappServices folder found in the configuration {config_folder_path}. You can use the script 'helpers/create_mapp_folders.py' to create the mapp folder structure in the Physical directory.")
                    if not mappMotion_path:
                        messages.append(f"No mappMotion folder found in the configuration {config_folder_path}. You can use the script 'helpers/create_mapp_folders.py' to create the mapp folder structure in the Physical directory.")
                    if not mappView_path:
                        messages.append(f"No mappView folder found in the configuration {config_folder_path}. You can use the script 'helpers/create_mapp_folders.py' to create the mapp folder structure in the Physical directory.")

    return messages
