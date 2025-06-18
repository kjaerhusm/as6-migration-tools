import os
import re
import hashlib
import sys

def calculate_file_hash(file_path):
    """
    Calculates the hash (MD5) of a file for comparison purposes.
    """
    md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        while chunk := f.read(4096):
            md5.update(chunk)
    return md5.hexdigest()

def replace_functions_and_constants(file_path, function_mapping, constant_mapping):
    """
    Replace function calls and constants in a file based on the provided mappings.
    """
    original_hash = calculate_file_hash(file_path)

    with open(file_path, "r", encoding="iso-8859-1", errors="ignore") as f:
        original_content = f.read()

    modified_content = original_content
    function_replacements = 0
    constant_replacements = 0

    for old_func, new_func in function_mapping.items():
        pattern = rf"\b{re.escape(old_func)}\s*\("
        replacement = f"{new_func}("
        modified_content, num_replacements = re.subn(pattern, replacement, modified_content)
        function_replacements += num_replacements

    for old_const, new_const in constant_mapping.items():
        pattern = rf"\b{re.escape(old_const)}\b"
        replacement = new_const
        modified_content, num_replacements = re.subn(pattern, replacement, modified_content)
        constant_replacements += num_replacements

    if modified_content != original_content:
        with open(file_path, "w", encoding="iso-8859-1") as f:
            f.write(modified_content)

        new_hash = calculate_file_hash(file_path)
        if original_hash == new_hash:
            return function_replacements, constant_replacements, False

        print(f"{function_replacements + constant_replacements:4d} changes written to: {file_path}")
        return function_replacements, constant_replacements, True

    return function_replacements, constant_replacements, False

def check_for_asmath_library(project_path):
    """
    Checks if AsMath library is used in the project.
    """
    pkg_file = os.path.join(project_path, "Logical", "Libraries", "Package.pkg")
    if not os.path.isfile(pkg_file):
        #print(f"Debug: Could not find Package.pkg file in: {pkg_file}")
        return False

    with open(pkg_file, "r", encoding="iso-8859-1", errors="ignore") as f:
        content = f.read()
        #print("Debug: Reading Package.pkg content...")
        #print(content)  # Show the content of Package.pkg for debugging

        if "AsMath" in content:
            print("AsMath library found in Package.pkg!\n")
            return True
        #else:
            #print("Debug: AsMath library not found in Package.pkg.")
    return False

def main():
    """
    Main function to replace AsMath functions and constants with their AsBrMath equivalents.
    """
    project_path = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()

    # Check if valid project path
    if not os.path.exists(project_path):
        print(f"Error: The provided project path does not exist: {project_path}")
        print("\nEnsure the path is correct and the project folder exists.")
        print("\nIf the path contains spaces, make sure to wrap it in quotes, like this:")
        print('   python asmath_to_asbrmath.py "C:\\path\\to\\your\\project"')
        sys.exit(1)

    # Check if .apj file exists in the provided path
    apj_files = [file for file in os.listdir(project_path) if file.endswith(".apj")]
    if not apj_files:
        print(f"Error: No .apj file found in the provided path: {project_path}")
        print("\nPlease specify a valid Automation Studio project path.")
        sys.exit(1)

    print(f"Project path validated: {project_path}")
    print(f"Using project file: {apj_files[0]}\n")

    logical_path = os.path.join(project_path, "Logical")

    print("Checking for AsMath library in the project...")
    library_found = check_for_asmath_library(project_path)

    if not library_found:
        print("AsMath library not found.")
        proceed = input("Do you want to proceed with replacing functions and constants anyway? (y/n): ").strip().lower()
        if proceed != 'y':
            print("Operation cancelled. No changes were made.")
            return
        print()

    print(
        "This script will search for usages of AsMath functions and constants and replace them with the AsBrMath equivalents.\n"
        "Before proceeding, make sure you have a backup or are using version control (e.g., Git).\n"
    )
    proceed = input("Do you want to continue? (y/n): ").strip().lower()
    if proceed != 'y':
        print("Operation cancelled. No changes were made.")
        return

    function_mapping = {
        "atan2": "brmatan2",
        "ceil": "brmceil",
        "cosh": "brmcosh",
        "floor": "brmfloor",
        "fmod": "brmfmod",
        "frexp": "brmfrexp",
        "ldexp": "brmldexp",
        "modf": "brmmodf",
        "pow": "brmpow",
        "sinh": "brmsinh",
        "tanh": "brmtanh",
    }

    constant_mapping = {
        "am2_SQRTPI": "brm2_SQRTPI",
        "amSQRT1_2": "brmSQRT1_2",
        "amSQRTPI": "brmSQRTPI",
        "amLOG2_E": "brmLOG2_E",
        "amLOG10E": "brmLOG10E",
        "amIVLN10": "brmINVLN10",
        "amINVLN2": "brmINVLN2",
        "amTWOPI": "brmTWOPI",
        "amSQRT3": "brmSQRT3",
        "amSQRT2": "brmSQRT2",
        "amLOG2E": "brmLOG2E",
        "amLN2LO": "brmLN2LO",
        "amLN2HI": "brmLN2HI",
        "am3PI_4": "brm3PI_4",
        "amPI_4": "brmPI_4",
        "amPI_2": "brmPI_2",
        "amLN10": "brmLN10",
        "am2_PI": "brm2_PI",
        "am1_PI": "brm1_PI",
        "amLN2": "brmLN2",
        "amPI": "brmPI",
        "amE": "brmE",
    }

    total_function_replacements = 0
    total_constant_replacements = 0
    total_files_changed = 0

    for root, _, files in os.walk(logical_path):
        for file in files:
            if file.endswith((".st")):
                file_path = os.path.join(root, file)
                function_replacements, constant_replacements, changed = replace_functions_and_constants(
                    file_path, function_mapping, constant_mapping
                )
                if changed:
                    total_function_replacements += function_replacements
                    total_constant_replacements += constant_replacements
                    total_files_changed += 1

    print("\nSummary:")
    print(f"Total functions replaced: {total_function_replacements}")
    print(f"Total constants replaced: {total_constant_replacements}")
    print(f"Total files changed: {total_files_changed}")

    if total_function_replacements == 0 and total_constant_replacements == 0:
        print("\nNo functions or constants needed to be replaced.")
    else:
        print("\nReplacement completed successfully.")

if __name__ == "__main__":
    main()
