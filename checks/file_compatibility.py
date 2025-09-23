import re
from pathlib import Path

from utils import utils


version_pattern = re.compile(r'AutomationStudio (?:Working)?Version="?([\d.]+)')


def check_file_version(file_path):
    """
    Checks the version of a given file
    """
    required_version_prefix = "4.12"

    result = set()
    content = utils.read_file(Path(file_path))
    version_match = version_pattern.search(content)
    if version_match:
        version = version_match.group(1)
        if not version.startswith(required_version_prefix):
            result.add((file_path, version))
    else:
        result.add((file_path, "Version Unknown"))
    return list(result)


def check_files_for_compatibility(project_path, log, verbose=False):
    """
    Checks the compatibility of .apj and .hw files within a apj_path.
    Validates that files have a minimum required version.
    Generates warning when files are converted to a new format in AS6 that may break references.
    """
    log("─" * 80 + "\nChecking project and hardware files for compatibility...")

    project_path = Path(project_path)
    physical_path = project_path / "Physical"

    results = utils.scan_files_parallel(project_path, [".apj"], check_file_version)
    results += utils.scan_files_parallel(physical_path, [".hw"], check_file_version)
    if results:
        log(
            "The following files are incompatible with the required version:",
            severity="MANDATORY",
        )
        output = ""
        for file_path, version in results:
            output += f"\n- {file_path}: {version}"
        log(output[1:])
        log(
            "Please ensure these files are saved at least once with Automation Studio 4.12",
            severity="MANDATORY",
        )
    else:
        if verbose:
            log("All project and hardware files are valid.", severity="VERBOSE")

    # --- Search for *.pkg files in config_folder and subfolders ---
    reference_files = []
    for path in physical_path.rglob("*.pkg"):
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
            "Some files are converted to a new format in AS6. This may break references, "
            "The following .pkg files contain file reference, make sure that the references are valid after converting to AS6:",
            severity="WARNING",
        )
        output = ""
        for ref_file in reference_files:
            output += f"\n- {ref_file}"
        log(output[1:])
