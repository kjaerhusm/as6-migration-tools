import os
import xml.etree.ElementTree as ET
from pathlib import Path


def check_uad_files(root_dir: Path, log, verbose=False):
    """
    Checks if .uad files are located in any directory ending with Connectivity/OpcUA.
    Returns a list of misplaced .uad files.

    Args:
        root_dir: Root directory of the project.
        log: Logging function to report issues.
        verbose: If True, logs additional information.

    Returns:
        Nothing
    """

    log("─" * 80 + "\nChecking OPC configuration...")

    required_suffix = os.path.normpath(os.path.join("Connectivity", "OpcUA"))
    misplaced_files = []
    old_version = []

    for path in root_dir.rglob("*.uad"):
        relative_parent = path.parent.relative_to(root_dir)
        if not str(relative_parent).endswith(str(required_suffix)):
            misplaced_files.append(str(path))

        try:
            tree = ET.parse(path)
            root_element = tree.getroot()
            file_version = int(root_element.attrib.get("FileVersion", 0))
            if file_version < 9:
                old_version.append(str(path))
        except Exception:
            pass

    if misplaced_files:
        log(
            "The following .uad files are not located in the required Connectivity/OpcUA directory:",
            when="AS4",
            severity="MANDATORY",
        )
        for file_path in misplaced_files:
            log(f"- {file_path}", severity="MANDATORY")
        log(
            "\nPlease create (via AS 4.12) and move these files to the required directory: Connectivity/OpcUA.",
            severity="MANDATORY",
        )
    else:
        if verbose:
            log("- All .uad files are in the correct location.", severity="INFO")

    if old_version:
        log(
            "The following .uad files do not have the minimum file version 9:",
            when="AS4",
            severity="MANDATORY",
        )
        for file_path in old_version:
            log(f"- {file_path}")
        log(
            "Please edit the uad file, make a small change and save the file to trigger the file update.",
            when="AS4",
            severity="MANDATORY",
        )
    else:
        if verbose:
            log("- All .uad files have the correct minimum version.", severity="INFO")
