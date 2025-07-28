import os
import re


def check_vision_settings(directory, log, verbose=False):
    """
    Checks for the presence of mappVision settings files in the specified directory.
    """
    found = False

    # Find the .apj file in the directory
    apj_file = None
    for file in os.listdir(directory):
        if file.endswith(".apj"):
            apj_file = os.path.join(directory, file)
            break

    if not apj_file:
        return found

    # If .apj file is found, check for mappVision line in the .apj file
    with open(apj_file, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if "<mappVision " in line and "Version=" in line:
                match = re.search(r'Version="(\d+)\.(\d+)', line)
                if match:
                    found = True
                    major = int(match.group(1))
                    minor = int(match.group(2))
                    version = f"{major}.{minor}"

                    log(
                        f"\n\nFound usage of mapp Vision (Version: {version}). After migrating to AS6 make sure that IP forwarding is activated under the Powerlink interface!",
                        when="AS6",
                        severity="WARNING",
                    )

    if verbose:
        # Walk through all directories
        for root, dirs, files in os.walk(os.path.join(directory, "Physical")):
            # Check if "mappVision" folder exists in current directory
            if "mappVision" in dirs:
                vision_path = os.path.join(root, "mappVision")
                log(f"mappVision folders found at: {vision_path}", severity="INFO")

    return found
