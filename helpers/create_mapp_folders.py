import argparse
import os
import sys
from lxml import etree

from utils import utils


def add_mapp_package(
    config_folder_path, subfolders, folder, package_name, package_type
):
    """
    Adds a mapp package (mappServices, mappMotion, mappView) to the cpu.pkg file and creates the folder structure.

    Args:
        config_folder_path (str): Path to the config folder
        subfolders (list): List of subfolders in the config folder
        folder (str): Name of the current folder being processed
        package_name (str): Name of the mapp package (e.g., 'mappServices', 'mappMotion', 'mappView')
        package_type (str):The package type to use for the attribute "PackageType" in Package.pkg
    """
    utils.log(f"\nStart fixing {package_name}")

    # Try to open and parse cpu.pkg as XML
    cpu_pkg_path = os.path.join(config_folder_path, subfolders[0], "cpu.pkg")
    if os.path.exists(cpu_pkg_path):
        try:
            tree = etree.parse(cpu_pkg_path)
            root = tree.getroot()

            # Try to find Objects node with different namespace approaches
            objects_node = None

            # Method 1: Try with default namespace
            ns_default = {"ns": "http://br-automation.co.at/AS/Cpu"}
            objects_node = root.find("ns:Objects", ns_default)

            # Method 2: If not found, try without namespace (for files with xmlns:ns0)
            if objects_node is None:
                objects_node = root.find("Objects")

            # Method 3: If still not found, try with ns0 prefix
            if objects_node is None:
                ns_prefixed = {"ns0": "http://br-automation.co.at/AS/Cpu"}
                objects_node = root.find("ns0:Objects", ns_prefixed)

            # Method 4: Last resort - search by local name (ignoring namespace)
            if objects_node is None:
                for child in root:
                    if child.tag.endswith("Objects"):
                        objects_node = child
                        break

            if objects_node is not None:
                utils.log_v(f"Found Objects node in cpu.pkg in {folder}")

                # Check if package object already exists
                existing_package = None

                # Try different methods to find Object elements
                object_elements = objects_node.findall("ns:Object", ns_default)
                if not object_elements:
                    object_elements = objects_node.findall("Object")
                if not object_elements:
                    ns_prefixed = {"ns0": "http://br-automation.co.at/AS/Cpu"}
                    object_elements = objects_node.findall("ns0:Object", ns_prefixed)
                if not object_elements:
                    # Last resort - find by local name
                    object_elements = [
                        child for child in objects_node if child.tag.endswith("Object")
                    ]

                for obj in object_elements:
                    if obj.text == package_name and obj.get("Type") == "Package":
                        existing_package = obj
                        utils.log_v(
                            f"{package_name} entry already exists in cpu.pkg in {folder}"
                        )
                        break

                if existing_package is None:
                    # Create new element without namespace prefix
                    new_object = etree.SubElement(objects_node, "Object")
                    new_object.set("Type", "Package")
                    new_object.text = package_name

                    # Save with pretty formatting
                    tree.write(
                        cpu_pkg_path,
                        encoding="utf-8",
                        xml_declaration=True,
                        pretty_print=True,
                    )
                    utils.log_v(f"Added {package_name} object to cpu.pkg in {folder}")
                else:
                    utils.log_v(
                        f"{package_name} object already exists in cpu.pkg in {folder}"
                    )
            else:
                utils.log("Objects node not found in cpu.pkg")
        except etree.ParseError as e:
            utils.log(f"Error parsing cpu.pkg XML in {folder}: {e}")
        except Exception as e:
            utils.log(f"Error opening cpu.pkg in {folder}: {e}")
    else:
        utils.log(f"cpu.pkg file not found in {config_folder_path}")

    # Check if package folder exists in the subfolders
    plc_folder_path = os.path.join(config_folder_path, subfolders[0], package_name)
    if os.path.exists(plc_folder_path):
        utils.log_v(f"Found {package_name} folder in {folder}")
        return True
    else:
        # Create package folder structure
        os.makedirs(plc_folder_path, exist_ok=True)
        utils.log_v(f"No {package_name} folder found")
        utils.log_v(f"Created {package_name} directory: {plc_folder_path}")

        # Create Package.pkg file with specified content
        package_content = f"""<?xml version="1.0" encoding="utf-8"?><?AutomationStudio FileVersion="4.9"?><Package SubType="{package_type}" PackageType="{package_type}" xmlns="http://br-automation.co.at/AS/Package"><Objects /></Package>"""
        package_file_path = os.path.join(plc_folder_path, "Package.pkg")
        with open(package_file_path, "w", encoding="utf-8") as f:
            f.write(package_content)

        utils.log_v(f"Created Package.pkg file in {package_file_path}")
        utils.log(f"{package_name} folder structure created successfully!")
        return False


def parse_args(argv):
    parser = argparse.ArgumentParser(description="Creates non existing mapp folders")
    parser.add_argument(
        "project_path",
        nargs="?",
        type=str,
        default=os.getcwd(),
        help="Automation Studio 4.x path containing *.apj file",
    )
    parser.add_argument("-v", "--verbose", action="store_true", required=False)

    return parser.parse_args()


def main():
    """
    Main function to add mapp folder structure to an Automation Studio project.
    """
    args = parse_args(sys.argv)
    project_path = args.project_path

    utils.set_verbose(args.verbose)

    # Check if valid project path
    if not os.path.exists(project_path):
        print(f"Error: The provided project path does not exist: {project_path}")
        sys.exit(1)

    # Check if .apj file exists in the provided path
    apj_files = [file for file in os.listdir(project_path) if file.endswith(".apj")]
    if not apj_files:
        utils.log(f"Error: No .apj file found in the provided path: {project_path}")
        utils.log("\nPlease specify a valid Automation Studio project path.")
        sys.exit(1)

    utils.log(f"Project path validated: {project_path}")
    utils.log(f"Using project file: {apj_files[0]}\n")

    # Get all folders in the Physical directory
    physical_path = os.path.join(project_path, "Physical")
    if os.path.exists(physical_path) and os.path.isdir(physical_path):
        physical_folders = [
            f
            for f in os.listdir(physical_path)
            if os.path.isdir(os.path.join(physical_path, f))
        ]

        for folder in physical_folders:
            config_folder_path = os.path.join(physical_path, folder)

            # Check if mappServices folder exists in the config folder directory
            if os.path.exists(config_folder_path):
                utils.log(f"\nFound configuration folder: {config_folder_path}")

                # Check for sub folders in the config folder
                subfolders = [
                    f
                    for f in os.listdir(config_folder_path)
                    if os.path.isdir(os.path.join(config_folder_path, f))
                ]

                if subfolders:
                    # Add mappServices package
                    mapp_services_exists = add_mapp_package(
                        config_folder_path,
                        subfolders,
                        folder,
                        "mappServices",
                        "mappServices",
                    )

                    # Add mappMotion package
                    mapp_motion_exists = add_mapp_package(
                        config_folder_path,
                        subfolders,
                        folder,
                        "mappMotion",
                        "mappMotion",
                    )

                    # Add mappView package
                    mapp_view_exists = add_mapp_package(
                        config_folder_path,
                        subfolders,
                        folder,
                        "mappView",
                        "mappViewControl",
                    )

        utils.log(
            f"\nPlease close and reopen the project in Automation Studio to see the changes."
        )


if __name__ == "__main__":
    main()
