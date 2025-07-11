import os
import re
import xml.etree.ElementTree as ET


def check_safety_release(project_root):
    """
    Checks if the project uses MappSafety or SafetyRelease.

    Returns:
        dict: Contains keys:
            - 'mode': 'mappsafety', 'safetyrelease', or 'none'
            - 'details': list of file paths or descriptions
    """
    result = {"mode": "none", "details": []}

    # 1. Check .apj file in root for MappSafety
    apj_path = None
    for file in os.listdir(project_root):
        if file.endswith(".apj"):
            apj_path = os.path.join(project_root, file)
            break

    if apj_path:
        try:
            tree = ET.parse(apj_path)
            root = tree.getroot()
            # Check <mappSafety Version="..."/>
            if root.find(".//{*}mappSafety") is not None:
                result["mode"] = "mappsafety"
                result["details"].append(
                    "Migrating from mapp Safety 5.x to mapp Safety 6.x - "
                    "All conversion steps are carried out automatically by the system; no action by the user is necessary."
                )
                return result  # Valid project
        except Exception as e:
            result["details"].append(f"Failed to parse .apj file: {e}")

    # 2. Search for *.pkg files containing 'SafetyRelease' with version != 0.0
    for root, _, files in os.walk(project_root):
        for file in files:
            if file.endswith(".pkg"):
                pkg_path = os.path.join(root, file)
                try:
                    with open(pkg_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        if 'SafetyRelease="' in content:
                            match = re.search(r'SafetyRelease="(\d+)\.(\d+)"', content)
                            if match and (
                                match.group(1) != "0" or match.group(2) != "0"
                            ):
                                result["mode"] = "safetyrelease"
                                result["details"].append(
                                    "Legacy safety is no longer supported with AS 6.x.\n"
                                    "When upgrading from a Safety Release to mapp Safety 6.x, all conversion steps from the Safety Release "
                                    "to mapp Safety 5.x must be performed in AS 4.x first.\n"
                                    "More info: https://help.br-automation.com/#/en/4/safety/mapp_safety/getting-started/proj-conversion/umstieg_auf_mapp_safety_5.x.html"
                                )
                                return result
                except Exception as e:
                    result["details"].append(f"Failed to read {pkg_path}: {e}")

    # 3. Check for *.swt files in Physical folders
    for root, _, files in os.walk(project_root):
        for file in files:
            if file.endswith(".swt"):
                swt_path = os.path.join(root, file)
                result["mode"] = "safetyrelease"
                result["details"].append(
                    f"Safety .swt file found but no SafetyRelease or MappSafety version found: {swt_path}"
                )
                return result

    return result


def check_safety(project_root):
    result = check_safety_release(project_root)
    findings = []

    if result["mode"] == "mappsafety":
        findings.extend(result["details"])
    elif result["mode"] == "safetyrelease":
        findings.extend(result["details"])
    else:
        findings.append("ℹ No safety system detected")

    return findings
