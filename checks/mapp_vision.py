import os

def check_vision_settings(directory):
    """
    Checks for the presence of mappVision settings files in the specified directory.

    Args:
        directory (str): Path to the directory to scan.

    Returns:
        dict: Contains information about mappVision settings found:
             - 'found': Boolean indicating if mappVision was found
             - 'locations': List of mappVision folder paths
             - 'total_files': Total number of files in all mappVision folders
    """
    vision_settings_result = {
        'found': False,
        'locations': [],
        'total_files': 0
    }
    
    # Walk through all directories
    for root, dirs, files in os.walk(directory):
        # Check if "mappVision" folder exists in current directory
        if "mappVision" in dirs:
            vision_path = os.path.join(root, "mappVision")
            vision_settings_result['found'] = True
            vision_settings_result['locations'].append(vision_path)
            
            # Count files in the mappVision folder and its subdirectories
            file_count = 0
            for sub_root, _, sub_files in os.walk(vision_path):
                file_count += len(sub_files)
            
            vision_settings_result['total_files'] += file_count
    
    return vision_settings_result