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

            utils.log(
                "Scanning started... Please wait while the script analyzes your project files.\n",
                file,
            )

            start_time = time.time()

            if not check_project_path_and_name(args.project_path, apj_file):
                log(
                    "Invalid path or project name, see "
                    "https://help.br-automation.com/#/en/6/revinfos/version-info/projekt_aus_automation_studio_4_ubernehmen/automation_studio/notwendige_anpassungen_im_automation_studio_4_projekt.html",
                    severity="ERROR",
                )

            logical_path = Path(args.project_path) / "Logical"
            physical_path = Path(args.project_path) / "Physical"

            file_patterns = [".apj", ".hw"]
            check_files_for_compatibility(
                args.project_path, file_patterns, log, args.verbose
            )

            check_uad_files(physical_path, log, args.verbose)

            check_hardware(physical_path, log, args.verbose, unsupported_hardware)

            check_file_devices(physical_path, log, args.verbose)

            check_libraries(
                logical_path, log, args.verbose, manual_process_libraries, obsolete_dict
            )

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
