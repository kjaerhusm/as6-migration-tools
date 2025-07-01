import os
import re

def check_mappView(directory):
    """
    Checks for the presence of mappView settings files in the specified directory.

    Args:
        directory (str): Path to the directory to scan.

    Returns:
        dict: Contains information about mappView settings found:
             - 'found': Boolean indicating if mappVision was found
             - 'version': Version of mappView if found
    """
    mappView_settings_result = {
        'found': False,
        'version': "",
        'locations': []
    }

    # Find the .apj file in the directory
    apj_file = None
    for file in os.listdir(directory):
        if file.endswith(".apj"):
            apj_file = os.path.join(directory, file)
            break
    
    if not apj_file:
        return mappView_settings_result

    # If .apj file is found, check for mappView line in the .apj file
    with open(apj_file, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if "<mappView " in line and "Version=" in line:
                match = re.search(r'Version="(\d+)\.(\d+)', line)
                if match:
                    major = int(match.group(1))
                    minor = int(match.group(2))
                    mappView_settings_result['found'] = True
                    mappView_settings_result['version'] = f"{major}.{minor}"
    
    # Walk through all directories
    for root, dirs, files in os.walk(os.path.join(directory, "Physical")):
        # Check if "mappView" folder exists in current directory and save its path
        if "mappView" in dirs:
            mappView_path = os.path.join(directory, "mappView")
            mappView_settings_result['locations'].append(mappView_path)
            
    return mappView_settings_result   