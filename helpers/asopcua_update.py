# The OPC UA client library in Automation Runtime 6 has been updated to OPC 30001 PLC client function blocks based on IEC 61131-3 1.2.
# To migrate a project from an older AR version to AR 6, modifications to the program are necessary.
import os
import re
import hashlib
import sys


def calculate_file_hash(file_path):
    """
    Calculates the hash (MD5) of a file for comparison purposes.
    """
    md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        while chunk := f.read(4096):
            md5.update(chunk)
    return md5.hexdigest()


def replace_enums(file_path, enum_mapping):
    """
    Replace enumerators in a file based on the provided mappings.
    """
    if "AsOpcUac" in file_path or "AsOpcUas" in file_path:
        return 0, False

    original_hash = calculate_file_hash(file_path)

    with open(file_path, "r", encoding="iso-8859-1", errors="ignore") as f:
        original_content = f.read()

    modified_content = original_content
    enum_replacements = 0

    # Replace enums
    for old_const, new_const in enum_mapping.items():
        pattern = re.escape(old_const)
        replacement = new_const
        modified_content, num_replacements = re.subn(
            pattern, replacement, modified_content
        )
        enum_replacements += num_replacements

    if modified_content != original_content:
        with open(file_path, "w", encoding="iso-8859-1") as f:
            f.write(modified_content)

        new_hash = calculate_file_hash(file_path)
        if original_hash == new_hash:
            return enum_replacements, False

        print(f"{enum_replacements :4d} changes written to: {file_path}")
        return enum_replacements, True

    return enum_replacements, False


def replace_fbs_and_types(file_path, fb_mapping, type_mapping):
    """
    Replace function block calls and types in a file based on the provided mappings.
    """
    if "AsOpcUac" in file_path or "AsOpcUas" in file_path:
        return 0, 0, False

    original_hash = calculate_file_hash(file_path)

    with open(file_path, "r", encoding="iso-8859-1", errors="ignore") as f:
        original_content = f.read()

    modified_content = original_content
    fb_replacements = 0
    type_replacements = 0

    # Replace function blocks
    for old_fb, new_fb in fb_mapping.items():
        pattern = rf"\b{re.escape(old_fb)}\b"
        replacement = new_fb
        modified_content, num_replacements = re.subn(
            pattern, replacement, modified_content
        )
        fb_replacements += num_replacements

    # Replace types
    for old_typ, new_typ in type_mapping.items():
        pattern = rf"\b{re.escape(old_typ)}\b"
        replacement = new_typ
        modified_content, num_replacements = re.subn(
            pattern, replacement, modified_content
        )
        type_replacements += num_replacements

    if modified_content != original_content:
        with open(file_path, "w", encoding="iso-8859-1") as f:
            f.write(modified_content)

        new_hash = calculate_file_hash(file_path)
        if original_hash == new_hash:
            return fb_replacements, type_replacements, False

        print(
            f"{fb_replacements + type_replacements:4d} changes written to: {file_path}"
        )
        return fb_replacements, type_replacements, True

    return fb_replacements, type_replacements, False


def check_for_library(project_path, library_names):
    """
    Checks if any specified library is used in the project.
    """
    pkg_file = os.path.join(project_path, "Logical", "Libraries", "Package.pkg")
    if not os.path.isfile(pkg_file):
        print(f"Error: Could not find Package.pkg file in: {pkg_file}")
        return []

    with open(pkg_file, "r", encoding="iso-8859-1", errors="ignore") as f:
        content = f.read()
        found_libraries = [lib for lib in library_names if lib in content]

    return found_libraries


def main():
    project_path = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()

    # Check if valid project path
    if not os.path.exists(project_path):
        print(f"Error: The provided project path does not exist: {project_path}")
        print("\nEnsure the path is correct and the project folder exists.")
        print(
            "\nIf the path contains spaces, make sure to wrap it in quotes, like this:"
        )
        print('   python asopcua_update.py "C:\\path\\to\\your\\project"')
        sys.exit(1)

    # Check if .apj file exists in the provided path
    apj_files = [file for file in os.listdir(project_path) if file.endswith(".apj")]
    if not apj_files:
        print(f"Error: No .apj file found in the provided path: {project_path}")
        print("\nPlease specify a valid Automation Studio project path.")
        sys.exit(1)

    print(f"Project path validated: {project_path}")
    print(f"Using project file: {apj_files[0]}\n")

    library_names = ["AsOpcUac", "AsOpcUas"]
    found_libraries = check_for_library(project_path, library_names)

    print(
        "This script will search for usages of AsOpcUac and AsOpcUas function blocks, types and enumerators and update the naming.\n"
        "Before proceeding, make sure you have a backup or are using version control (e.g., Git).\n"
    )

    if __name__ == "__main__" and sys.stdin.isatty():

        if not found_libraries:
            print("Neither AsOpcUac nor AsOpcUas libraries found.\n")
            proceed = (
                input(
                    "Do you want to proceed with replacing functions and constants anyway? (y/n) [y]: "
                )
                .strip()
                .lower()
            )
            if proceed not in ("", "y"):
                print("Operation cancelled. No changes were made.")
                return
        else:
            print(f"Libraries found: {', '.join(found_libraries)}.\n")
            proceed = input("Do you want to continue? (y/n) [y]: ").strip().lower()
            if proceed not in ("", "y"):
                print("Operation cancelled. No changes were made.")
                return

    fb_mapping = {
        "UA_EventItemOperate": "UA_EventItemOperateList",
        "UA_EventItemRemove": "UA_EventItemRemoveList",
        "UA_GetNamespaceIndex": "UA_NamespaceGetIndex",
        "UA_MonitoredItemAdd": "UA_MonitoredItemAddList",
        "UA_MonitoredItemRemove": "UA_MonitoredItemRemoveList",
        "UA_MonitoredItemOperate": "UA_MonitoredItemOperateList",
        "UaClt_ReadBulk": "BrUa_ReadBulk",
        "UaClt_WriteBulk": "BrUa_WriteBulk",
    }

    type_mapping = {
        "UAArrayLength": "BrUaArrayLength",
        "UAByteString": "BrUaByteString",
        "UADataValue": "BrUaDataValue",
        "UAEUInformation": "BrUaEUInformation",
        "UAMethodArgument": "BrUaMethodArgument",
        "UAMonitoringParameters": "UAMonitoringParameter",
        "UAMonitoringSettings": "UAMonitoringParameter",
        "UANoOfElements": "BrUaNoOfElements",
        "UARange": "BrUaRange",
        "UATimeZoneData": "BrUaTimeZoneDataType",
        "UAVariantType": "BrUaVariantType",
    }

    enum_mapping = {
        "UAAttributeId": "UAAttributeID",
        "UAIdentifierType_String": "UAIT_String",
        "UAIdentifierType_Numeric": "UAIT_Numeric",
        "UAIdentifierType_GUID": "UAIT_GUID",
        "UAIdentifierType_Opaque": "UAIT_Opaque",
        "UASecurityMsgMode_": "UASMM_",
        "UASecurityPolicy_": "UASP_",
        "UAVariantType_": "BrUaVariantType_",
        "UADeadbandType_None": "UADT_None",
        "UADeadbandType_Absolute": "UADT_Absolute",
        "UADeadbandType_Percentt": "UADT_Percentt",
    }

    logical_path = os.path.join(project_path, "Logical")
    total_function_replacements = 0
    total_enums_replacements = 0
    total_type_replacements = 0
    total_files_changed = 0

    # Loop through the files in the "Logical" directory and process .st, .c, .cpp and .ab files
    for root, _, files in os.walk(logical_path):
        for file in files:
            if file.endswith((".st", ".c", ".cpp", ".ab")):
                file_path = os.path.join(root, file)
                enum_replacements, changed = replace_enums(file_path, enum_mapping)
                if changed:

                    total_enums_replacements += enum_replacements
                    total_files_changed += 1
            elif (
                file.endswith((".typ"))
                or file.endswith((".var"))
                or file.endswith((".fun"))
            ):
                file_path = os.path.join(root, file)
                function_replacements, type_replacements, changed = (
                    replace_fbs_and_types(file_path, fb_mapping, type_mapping)
                )
                if changed:
                    total_type_replacements += type_replacements
                    total_function_replacements += function_replacements
                    total_files_changed += 1

    print("\nSummary:")
    print(f"Total function blocks replaced: {total_function_replacements}")
    print(f"Total enumerators replaced: {total_enums_replacements}")
    print(f"Total types replaced: {total_type_replacements}")
    print(f"Total files changed: {total_files_changed}")

    if (
        total_function_replacements == 0
        and total_enums_replacements == 0
        and total_type_replacements == 0
    ):
        print("No functions or constants needed to be replaced.")
    else:
        print("Replacement completed successfully.")


if __name__ == "__main__":
    main()
