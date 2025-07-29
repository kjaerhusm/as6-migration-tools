import os
import sys
import re
import time
import json
import argparse
from pathlib import Path

from checks import *
from utils import utils

# path to the current script
script_directory = Path(__file__).resolve().parent

# files containing discontinuation information
discontinuation_info = {
    "obsolete_libs": {},
    "manual_process_libs": {},
    "obsolete_fbks": {},
    "obsolete_funcs": {},
    "unsupported_hw": {},
    "deprecated_string_functions": {},
    "deprecated_math_functions": {},
}

try:
    discontinuation_dir = Path(script_directory) / "discontinuations"
    for filename in discontinuation_info:
        file_path = discontinuation_dir / f"{filename}.json"
        with file_path.open("r", encoding="utf-8") as json_file:
            discontinuation_info[filename] = json.load(json_file)
except Exception as e:
    print(
        f"\033[1;31m[ERROR]\033[0m Error reading discontinuation lists: {e}",
        file=sys.stderr,
    )
    sys.exit(1)

# obsolete libraries with reasons
obsolete_dict = discontinuation_info["obsolete_libs"]
# Libraries that must be handled manually
manual_process_libraries = discontinuation_info["manual_process_libs"]
# list of obsolete function blocks with reasons
obsolete_function_blocks = discontinuation_info["obsolete_fbks"]
# Hardcoded list of obsolete functions with reasons
obsolete_functions = discontinuation_info["obsolete_funcs"]
# hardware not supported by >= 6.0
unsupported_hardware = discontinuation_info["unsupported_hw"]
# deprecated string functions 8 bit and 16 bit
deprecated_string_functions = set(discontinuation_info["deprecated_string_functions"])
# deprecated math functions
deprecated_math_functions = set(discontinuation_info["deprecated_math_functions"])

pass


def process_stub(file_path, *args):
    """
    Stub process function for demonstration purposes.
    Simulates processing of files without actual logic.

    Args:
        file_path (str): The file path to process.
        *args: Additional arguments.

    Returns:
        list: An empty list for this stub function.
    """
    return []


def scan_files_parallel(root_dir, extensions, process_function, *args):
    return utils.scan_files_parallel(root_dir, extensions, process_function, *args)


def process_pkg_file(file_path, patterns):
    """
    Processes a .pkg file to find matches for obsolete libraries.

    Args:
        file_path (str): Path to the .pkg file.
        patterns (dict): Patterns to match with reasons.

    Returns:
        list: Matches found in the file.
    """
    results = []
    content = Path(file_path).read_text(encoding="utf-8", errors="ignore")

    # Regex for library names between > and <
    matches = re.findall(r">([^<]+)<", content, re.IGNORECASE)
    for match in matches:
        for pattern, reason in patterns.items():
            if match.lower() == pattern.lower():
                results.append((pattern, reason, file_path))
    return results


def process_lby_file(file_path, patterns):
    """
    Processes a .lby file to find obsolete dependencies.

    Args:
        file_path (str): Path to the .lby file.
        patterns (dict): Patterns of obsolete dependencies with reasons.

    Returns:
        list: Matches found in the file in the format (library_name, dependency, reason, file_path).
    """
    results = []
    content = Path(file_path).read_text(encoding="utf-8", errors="ignore")

    # Extract library name (directory name as identifier)
    library_name = os.path.basename(os.path.dirname(file_path))
    # Extract dependencies from the XML content
    dependencies = re.findall(
        r'<Dependency ObjectName="([^"]+)"', content, re.IGNORECASE
    )
    for dependency in dependencies:
        for pattern, reason in patterns.items():
            # Compare case-insensitively
            if dependency.lower() == pattern.lower():
                results.append((library_name, dependency, reason, file_path))
    return results


def process_c_cpp_hpp_includes_file(file_path, patterns):
    """
    Processes a C, C++, or header (.hpp) file to find obsolete dependencies in #include statements.

    Args:
        file_path (str): Path to the file.
        patterns (dict): Dictionary of obsolete libraries with reasons.

    Returns:
        list: Matches found in the file in the format (library_name, reason, file_path).
    """
    results = []
    include_pattern = re.compile(r'#include\s+[<"]([^">]+)[">]')
    content = Path(file_path).read_text(encoding="utf-8", errors="ignore")

    for line in content:
        match = include_pattern.search(line)
        if match:
            included_library = match.group(1).lower()  # Normalize case
            for pattern, reason in patterns.items():
                if included_library == f"{pattern.lower()}.h":
                    results.append((pattern, reason, file_path))
    return results


# Function to process libraries requiring manual process
def process_manual_libraries(file_path, patterns):
    """
    Processes .pkg or .lby files to find libraries that require manual action during migration.

    Args:
        file_path (str): Path to the file.
        patterns (dict): Libraries to be checked for manual process.

    Returns:
        list: Matches found in the file.
    """
    results = []
    content = Path(file_path).read_text(encoding="utf-8", errors="ignore")

    matches = re.findall(r">([^<]+)<", content, re.IGNORECASE)
    for match in matches:
        for library, action in patterns.items():
            if match.lower() == library.lower():
                results.append((library, action, file_path))
    return results


def parse_args():
    parser = argparse.ArgumentParser(
        prog=os.path.basename(__file__),
        description="Scans Automation Studio project for transition from AS4 to AS6",
        usage="python %(prog)s project_path [options]",
        epilog="Ensure the path is correct and the project folder exists.\n"
        "A valid AS 4 project folder must contain an *.apj file.\n"
        'If the path contains spaces, make sure to wrap it in quotes (e.g. like this: "C:\\My documents\\project")\n'
        "If you enter a  '.' as project_path the current directory will be used.\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    # Add arguments
    parser.add_argument(
        "project_path",
        type=str,
        help="Automation Studio 4.x path containing *.apj file",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        required=False,
        help="Outputs verbose information",
    )
    # Parse the arguments

    # Fallback if no arguments are provided (e.g. when run from GUI)
    if len(sys.argv) == 1:
        # Default to current directory as project path
        sys.argv += [".", "-v"]
        # Optionally enable verbose mode by default from GUI
        # sys.argv += ["-v"]

    return parser.parse_args()


# Check the project name and path for invalid characters
# As opposed to what's in the help, we need to allow : and \ and / as well since these are valid
# path separators
def check_project_path_and_name(path, name):
    project_name_pattern = r"^(\w+)\.apj$"
    project_path_pattern = r"^[\w :\\/!(){}+\-@\.\^=]+$"
    return re.fullmatch(project_path_pattern, path) and re.fullmatch(
        project_name_pattern, name
    )


# Update main function to handle project directory input and optional verbose flag
def main():
    """
    Main function to scan for obsolete libraries, function blocks, functions, and unsupported hardware.
    Outputs the results to a file as well as the console.
    """

    build_number = utils.get_build_number()
    print(f"Script build number: {build_number}")

    args = parse_args()
    apj_file = utils.get_and_check_project_file(args.project_path)

    utils.set_verbose(args.verbose)

    print(f"Project path validated: {args.project_path}")
    print(f"Using project file: {apj_file}")

    output_file = os.path.join(args.project_path, "as4_to_as6_analyzer_result.txt")
    with open(output_file, "w", encoding="utf-8") as file:
        try:

            def log(message, when="", severity=""):
                utils.log(message, log_file=file, when=when, severity=severity)

            def log_v(message, log_file=file, prepend=""):
                utils.log_v(message, log_file, prepend)

            utils.log(
                "Scanning started... Please wait while the script analyzes your project files.\n",
                file,
            )

            start_time = time.time()

            if not check_project_path_and_name(args.project_path, apj_file):
                log(
                    "Invalid path or project name, see "
                    "https://help.br-automation.com/#/en/6/revinfos/version-info/projekt_aus_automation_studio_4_ubernehmen/automation_studio/notwendige_anpassungen_im_automation_studio_4_projekt.html"
                )

            logical_path = Path(args.project_path) / "Logical"
            physical_path = Path(args.project_path) / "Physical"

            # Use project_path as the root directory for scanning
            manual_libs_results = scan_files_parallel(
                logical_path,
                [".pkg"],
                process_manual_libraries,
                manual_process_libraries,
            )

            invalid_pkg_files = scan_files_parallel(
                logical_path,
                [".pkg"],
                process_pkg_file,
                obsolete_dict,
            )

            lby_dependency_results = scan_files_parallel(
                logical_path,
                [".lby"],
                process_lby_file,
                obsolete_dict,
            )

            c_include_dependency_results = scan_files_parallel(
                logical_path,
                [".c", ".cpp", ".hpp"],
                process_c_cpp_hpp_includes_file,
                obsolete_dict,
            )

            file_patterns = [".apj", ".hw"]
            check_files_for_compatibility(
                args.project_path, file_patterns, log, args.verbose
            )

            check_uad_files(physical_path, log, args.verbose)

            check_hardware(physical_path, log, args.verbose, unsupported_hardware)

            check_file_devices(physical_path, log, args.verbose)

            log("\n\nThe following invalid libraries were found in .pkg files:")
            if invalid_pkg_files:
                for library, reason, file_path in invalid_pkg_files:
                    log(f"- {library}: {reason} (Found in: {file_path})")
            else:
                log_v("- None")

            log(
                "\n\nThe following libraries might require manual action after migrating the project to Automation Studio 6:"
            )
            if manual_libs_results:
                for library, reason, file_path in manual_libs_results:
                    log(f"- {library}: {reason} (Found in: {file_path})")
            else:
                log_v("- None")

            # Convert .lby results to match the (library_name, reason, file_path) format
            normalized_lby_results = [
                (lib, f"Dependency on {dep}: {reason}", path)
                for lib, dep, reason, path in lby_dependency_results
            ]

            # Merge results from .lby and C/C++/HPP include dependencies
            all_dependency_results = (
                normalized_lby_results + c_include_dependency_results
            )

            log(
                "\n\nThe following obsolete dependencies were found in .lby, .c, .cpp, and .hpp files:"
            )
            if all_dependency_results:
                for library_name, reason, file_path in all_dependency_results:
                    log(f"- {library_name}: {reason} (Found in: {file_path})")
            else:
                log_v("- None")

            check_functions(
                args.project_path,
                log,
                args.verbose,
                obsolete_function_blocks,
                obsolete_functions,
                deprecated_string_functions,
                deprecated_math_functions,
            )

            # Find Safety system issues
            check_safety(args.project_path, log, args.verbose)

            # Find mappVision issues
            check_vision_settings(args.project_path, log, args.verbose)

            # Find mappView issues
            check_mappView(args.project_path, log, args.verbose)

            # Find mappService issues
            check_mapp_version(args.project_path, log, args.verbose)

            # Finish up
            end_time = time.time()
            log(
                "─" * 80
                + f"\nScanning completed successfully in {end_time - start_time:.2f} seconds."
            )

        except Exception as e:
            error_message = f"An unexpected error occurred: {str(e)}"
            log(error_message, severity="ERROR")

            # Ensure log file is open before writing
            try:
                with open(output_file, "a", encoding="utf-8") as error_log:
                    error_log.write(f"\n[ERROR] {error_message}\n")
            except Exception as log_error:
                log(f"Failed to write error to log file: {log_error}", severity="ERROR")

    utils.log(f"Results have been saved to {output_file}\n", log_file=None)


if __name__ == "__main__":
    main()
