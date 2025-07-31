import re


def check_mapp_version(apj_path, log, verbose=False):
    """
    Checks for the mapp Services version in the .apj project file.
    """

    log("─" * 80 + "\nChecking mapp version in project file...")

    # If no .apj file is found, return an empty list
    for line in apj_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        # Check for mapp Services version in the .apj file
        if ("<mapp " in line and "Version=" in line) or (
            "<mappServices" in line and "Version=" in line
        ):
            match = re.search(r'Version="(\d+)\.(\d+)', line)
            if match:
                # Extract major and minor version numbers
                major, minor = int(match.group(1)), int(match.group(2))
                version_str = f"{major}.{minor}"
                log(f"Detected Mapp Services version: {version_str}", severity="INFO")

                if major == 5 and minor < 20:
                    log(
                        "\nIt is recommended to use a mapp Services version 5.20 or later for the conversion."
                        "\nIf a mapp Services version older than 5.20 is used, the correct conversion of all configuration parameters is not guaranteed."
                        "\nPlease update the mapp Services version in AS4 to 5.20 or later before migrating to AS6.",
                        when="AS4",
                        severity="MANDATORY",
                    )
                else:
                    log(
                        "\nThe automatic mapp Services configuration upgrade is only available with mapp Services 6.0."
                        "\nPlease ensure the project is converted using AS6 and mapp Services 6.0 before upgrading to newer mapp versions.",
                        when="AS6",
                        severity="MANDATORY",
                    )

        # Check for mappMotion version 5.x
        if "<mappMotion " in line and 'Version="5.' in line:
            match = re.search(r'Version="(\d+)\.(\d+)', line)
            if match:
                major, minor = int(match.group(1)), int(match.group(2))
                version_str = f"{major}.{minor}"
                log(f"Detected Mapp Motion version: {version_str}", severity="INFO")
                log(
                    "\nYou must first upgrade mappMotion to version 6.0 using 'Change runtime versions' in AS6."
                    "\nOnce mappMotion 6.0 is set, a dialog will assist with converting all project configurations.",
                    when="AS6",
                    severity="MANDATORY",
                )

    # Make sure all mapp folders are present in the Physical directory
    # Get all folders in the Physical directory
    physical_path = apj_path.parent / "Physical"
    if not physical_path.is_dir():
        log(f"Could not find Physical in {apj_path.parent}", severity="ERROR")
        return

    # Check if relevant mapp folders exists in the config folder directory
    mapp_folders_to_check = ["mappServices", "mappMotion", "mappView", "mappCockpit"]

    grouped_results = {}
    config_folders = [f for f in physical_path.iterdir() if f.is_dir()]
    for config_folder in config_folders:
        # Check for sub folders in the config folder
        subfolders = [f for f in config_folder.iterdir() if f.is_dir()]
        if not subfolders:
            continue

        found_mapp_folders = {folder: False for folder in mapp_folders_to_check}

        # Walk through all directories
        start_path = subfolders[0]
        for path in start_path.rglob("*"):
            if path.is_dir() and path.name in mapp_folders_to_check:
                found_mapp_folders[path.name] = True

        missing = {name for name, found in found_mapp_folders.items() if not found}
        if missing:
            # Check Cpu.pkg file for referenced packages
            cpu_pkg_path = start_path / "Cpu.pkg"
            if cpu_pkg_path.exists():
                try:
                    cpu_pkg_content = cpu_pkg_path.read_text(
                        encoding="utf-8", errors="ignore"
                    )
                    missing_copy = missing.copy()  # Create a copy to iterate over

                    for line in cpu_pkg_content.splitlines():
                        for missing_item in missing_copy:
                            if missing_item in line and 'Reference="true"' in line:
                                # Remove from missing set if found with Reference="true"
                                if verbose:
                                    log(
                                        f"Removing '{missing_item}' from missing set, found reference in Cpu.pkg",
                                        when="AS4",
                                        severity="INFO",
                                    )
                                missing.discard(missing_item)
                except Exception as e:
                    log(f"Could not read Cpu.pkg file: {e}", severity="WARNING")

            # Only add to results if there are still missing folders after checking Cpu.pkg
            if missing:
                grouped_results[config_folder.name] = missing

    if grouped_results:
        message = "\nSome configurations are missing one or more of the mapp folders"
        for config_name, missing_mapp_folders in grouped_results.items():
            missing_folders = ", ".join(sorted(missing_mapp_folders))
            message += f"\n  - '{config_name}': {missing_folders}"

        message += "\n\nYou can use the script 'helpers/create_mapp_folders.py' to create the mapp folder structure in the Physical directory."
        log(message, when="AS4", severity="MANDATORY")
