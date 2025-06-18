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
            if "<mapp " in line and "Version=" in line:
                match = re.search(r'Version="(\d+)\.(\d+)', line)
                if match:
                    major = int(match.group(1))
                    minor = int(match.group(2))
                    version_str = f"{major}.{minor}"
                    messages.append(f"Detected Mapp Services version: {version_str}")
                    if major == 5 and minor < 20:
                        messages.append("It is recommended to use a mapp Services version 5.20 or later for the conversion.")
                        messages.append("If a mapp Services version older than 5.20 is used, the correct conversion of all configuration parameters is not guaranteed.")
                        messages.append("Please update the mapp Services version in AS4 to 5.20 or later before migrating to AS6.")
                    messages.append("The automatic mapp Services configuration upgrade is only available with mapp Services 6.0.")
                    messages.append("Please ensure the project is converted using AS6 and mapp Services 6.0 before upgrading to newer mapp versions.\n")

            # Check for mappMotion version 5.x
            if "<mappMotion " in line and 'Version="5.' in line:
                messages.append("Detected Mapp Motion version: 5.x")
                messages.append("You must first upgrade mappMotion to version 6.0 using 'Change runtime versions' in AS6.")
                messages.append("Once mappMotion 6.0 is set, a dialog will assist with converting all project configurations.")

    return messages
