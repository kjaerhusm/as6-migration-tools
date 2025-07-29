import os
import sys
import time
import argparse
from pathlib import Path

from checks import *
from utils import utils


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


# Update main function to handle project directory input and optional verbose flag
def main():
    """
    Main function to scan for obsolete libraries, function blocks, functions, and unsupported hardware.
    Outputs the results to a file as well as the console.
    """

    build_number = utils.get_build_number()
    utils.log(f"Script build number: {build_number}")

    args = parse_args()
    apj_file = utils.get_and_check_project_file(args.project_path)

    utils.log(f"Project path validated: {args.project_path}")
    utils.log(f"Using project file: {apj_file}")

    output_file = os.path.join(args.project_path, "as4_to_as6_analyzer_result.txt")
    with open(output_file, "w", encoding="utf-8") as file:
        try:

            def log(message, when="", severity=""):
                utils.log(message, log_file=file, when=when, severity=severity)

            log(
                "Scanning started... Please wait while the script analyzes your project files.",
            )

            start_time = time.time()

            check_project_path_and_name(args.project_path, apj_file, log, args.verbose)

            logical_path = Path(args.project_path) / "Logical"
            physical_path = Path(args.project_path) / "Physical"

            file_patterns = [".apj", ".hw"]
            check_files_for_compatibility(
                args.project_path, file_patterns, log, args.verbose
            )

            check_uad_files(physical_path, log, args.verbose)

            check_hardware(physical_path, log, args.verbose)

            check_file_devices(physical_path, log, args.verbose)

            check_libraries(logical_path, log, args.verbose)

            check_functions(
                args.project_path,
                log,
                args.verbose,
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
