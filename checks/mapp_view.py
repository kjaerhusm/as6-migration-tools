import os

def check_mappView(directory):
    """
    Checks for the presence of mappView settings files in the specified directory.

    Args:
        directory (str): Path to the directory to scan.

    Returns:
        dict: Contains information about mappView settings found:
             - 'found': Boolean indicating if mappVision was found
             - 'locations': List of mappView folder paths
    """
    mappView_settings_result = {
        'found': False,
        'locations': []
    }

    # Walk through all directories
    for root, dirs, files in os.walk(directory):
        # Check if "mappVision" folder exists in current directory
        if "mappView" in dirs:
            mappView_path = os.path.join(directory, "mappView")
            mappView_settings_result['found'] = True
            mappView_settings_result['locations'].append(mappView_path)
            
    return mappView_settings_result   