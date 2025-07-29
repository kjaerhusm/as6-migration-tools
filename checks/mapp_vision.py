import re
from pathlib import Path


def check_vision_settings(directory, log, verbose=False):
    """
    Checks for the presence of mappVision settings files in the specified directory.
    """
    log("─" * 80 + "\nChecking mappVision version in project file...")

    # Find the .apj file in the directory
    apj_file = next(Path(directory).glob("*.apj"), None)
    if not apj_file:
        log(f"Could no open apj file", severity="ERROR")
        return

    # If .apj file is found, check for mappVision line in the .apj file
    with Path(apj_file).open(encoding="utf-8", errors="ignore") as f:
        for line in f:
            if "<mappVision " in line and "Version=" in line:
                match = re.search(r'Version="(\d+)\.(\d+)', line)
                if match:
                    major = int(match.group(1))
                    minor = int(match.group(2))
                    version = f"{major}.{minor}"

                    log(f"Found usage of mapp Vision (Version: {version})", severity="INFO")
                    log(
                        f"After migrating to AS6 make sure that IP forwarding is activated under the Powerlink interface!",
                        when="AS6",
                        severity="MANDATORY",
                    )

    if verbose:
        # Walk through all directories
        for vision_path in Path(directory, "Physical").rglob("mappVision"):
            if vision_path.is_dir():
                log(f"mappVision folders found at: {vision_path}", severity="INFO")