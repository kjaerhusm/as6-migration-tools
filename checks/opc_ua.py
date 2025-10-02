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

    # Find misplaced and old opc ua files
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

    # report misplaced files
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

    # report old opc ua file version
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

    # Check for OPC UA activation in hardware files
    # Search in subdirectories for .hw files
    for subdir in root_dir.iterdir():
        if subdir.is_dir():
            for hw_file in subdir.rglob("*.hw"):
                if hw_file.is_file():
                    try:
                        tree = ET.parse(hw_file)
                        root_element = tree.getroot()
                        # Search for Parameter with ID="ActivateOpcUa" and Value="1" anywhere in the XML tree
                        # Handle default XML namespace if present (e.g., xmlns="http://br-automation.co.at/AS/Hardware")
                        ns = {}
                        if root_element.tag.startswith("{"):
                            ns_uri = root_element.tag.split("}", 1)[0][1:]
                            ns = {"as": ns_uri}
                            xpath = ".//as:Parameter[@ID='ActivateOpcUa'][@Value='1']"
                            matches = root_element.findall(xpath, ns)
                        else:
                            xpath = ".//Parameter[@ID='ActivateOpcUa'][@Value='1']"
                            matches = root_element.findall(xpath)

                        if matches:
                            log(
                                f"OPC UA model 1 is activated in {hw_file}. OPC UA model 1 is not supported in AS6 and will be automatically converted to model 2. This changes the namespace ID for variables.",
                                severity="INFO",
                            )
                    except Exception:
                        # Skip files that can't be parsed as XML
                        continue
