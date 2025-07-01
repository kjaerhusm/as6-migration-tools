import os
import re

def check_vision_settings(directory):
    """
    Checks for the presence of mappVision settings files in the specified directory.

    Args:
        directory (str): Path to the directory to scan.

    Returns:
        dict: Contains information about mappVision settings found:
             - 'found': Boolean indicating if mappVision was found
             - 'version': Version of mappVision if found
             - 'locations': List of mappVision folder paths
             - 'total_files': Total number of files in all mappVision folders
    """
    vision_settings_result = {
        'found': False,
        'version': "",
        'locations': [],
        'total_files': 0
    }

    # Find the .apj file in the directory
    apj_file = None
    for file in os.listdir(directory):
        if file.endswith(".apj"):
            apj_file = os.path.join(directory, file)
            break
    
    if not apj_file:
        return vision_settings_result
    
    # If .apj file is found, check for mappVision line in the .apj file
    with open(apj_file, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if "<mappVision " in line and "Version=" in line:
                match = re.search(r'Version="(\d+)\.(\d+)', line)
                if match:
                    major = int(match.group(1))
                    minor = int(match.group(2))
                    vision_settings_result['found'] = True
                    vision_settings_result['version'] = f"{major}.{minor}"
    
    # Walk through all directories
    for root, dirs, files in os.walk(directory):
        # Check if "mappVision" folder exists in current directory
        if "mappVision" in dirs:
            vision_path = os.path.join(root, "mappVision")
            vision_settings_result['locations'].append(vision_path)
            
            # Count files in the mappVision folder and its subdirectories
            file_count = 0
            for sub_root, _, sub_files in os.walk(vision_path):
                file_count += len(sub_files)
            
            vision_settings_result['total_files'] += file_count
    
    return vision_settings_result