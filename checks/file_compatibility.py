import re
from pathlib import Path

from utils import utils


def check_files_for_compatibility(apj_path, extensions, log, verbose=False):
    """
    Checks the compatibility of .apj and .hw files within a apj_path.
    Validates that files have a minimum required version.
    Generates warning when files are converted to a new format in AS6 that may break references.
    """
    log("─" * 80 + "\nChecking project and hardware files for compatibility...")

    incompatible_files = []
    required_version_prefix = "4.12"
    version_pattern = re.compile(r'AutomationStudio (?:Working)?Version="?([\d.]+)')

    for ext in extensions:
        for path in Path(apj_path).rglob(f"*{ext}"):
            if path.is_file():
                content = utils.read_file(path)
                version_match = version_pattern.search(content)
                if version_match:
                    version = version_match.group(1)
                    if not version.startswith(required_version_prefix):
                        incompatible_files.append((str(path), f"Version {version}"))
                else:
                    incompatible_files.append((str(path), "Version Unknown"))

    if incompatible_files:
        log(
            "The following files are incompatible with the required version:",
            severity="MANDATORY",
        )
        for file_path, issue in incompatible_files:
            log(f"- {file_path}: {issue}")
        log(
            "Please ensure these files are saved at least once with Automation Studio 4.12",
            severity="MANDATORY",
        )
        return False
    else:
        if verbose:
            log("All project and hardware files are valid.", severity="VERBOSE")

    # --- Search for *.pkg files in config_folder and subfolders ---
    reference_files = []
    for path in Path(apj_path + "/Physical").rglob("*.pkg"):
        # Ignore files in any directory named 'mappView'
        if "mappView" in path.parts:
            continue
        if path.is_file():
            try:
                import xml.etree.ElementTree as ET

                tree = ET.parse(path)
                root = tree.getroot()
                # Search for any node with Type="File" and Reference="true" attributes
                found = False
                for elem in root.iter():
                    if (
                        elem.attrib.get("Type") == "File"
                        and elem.attrib.get("Reference") == "true"
                    ):
                        found = True
                        break
                if found:
                    reference_files.append(str(path))
            except Exception as e:
                # Fallback: ignore file if not valid XML
                pass

    if reference_files:
        log(
            "Some files are converted to a new format in AS6. This may break references, The following .pkg files contain file reference, make sure that the references are valid after converting to AS6:",
            severity="WARNING",
        )
        for ref_file in reference_files:
            log(f"- {ref_file}")

    return True
