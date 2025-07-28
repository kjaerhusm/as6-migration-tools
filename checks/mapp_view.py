import re
from pathlib import Path


def check_mappView(directory, log, verbose=False):
    """
    Checks for the presence of mappView settings files in the specified directory.

    Args:
        directory (str): Path to the directory to scan.

    Returns:
        Nothing
    """
    directory = Path(directory)

    # Find the .apj file in the directory
    apj_file = next(directory.glob("*.apj"), None)
    if not apj_file:
        return found_mappView

    # If .apj file is found, check for mappView line in the .apj file
    for line in apj_file.read_text(encoding="utf-8", errors="ignore").splitlines():
        if "<mappView " in line and "Version=" in line:
            match = re.search(r'Version="(\d+)\.(\d+)', line)
            if match:
                major = int(match.group(1))
                minor = int(match.group(2))
                version = f"{major}.{minor}"

                log(
                    f"\n\nFound usage of mappView (Version: {version}). Several security settings will be enforced after the migration."
                    "\n"
                    "\n- To allow access without a certificate"
                    "\n  Change the following settings in the OPC Client/Server configuration (Configuration View/Connectivity/OpcUaCs/UaCsConfig.uacfg):"
                    "\n  ClientServerConfiguration->Security->MessageSecurity->SecurityPolicies->None: Enabled"
                    "\n"
                    "\n- User login will be enabled by default. To allow anonymous access"
                    "\n  Change the following settings in mappView configuration (Configuration View/mappView/Config.mappviewcfg):"
                    "\n  MappViewConfiguration->Server Configuration->Startup User: anonymous token"
                    "\n"
                    "\n- Change the following settings in the OPC Client/Server configuration (Configuration View/Connectivity/OpcUaCs/UaCsConfig.uacfg):"
                    "\n  ClientServerConfiguration->Security->Authentication->Authentication Methods->Anymous: Enabled"
                    "\n"
                    "\n- Change the following settings in the User role system (Configuration View/AccessAndSecurity/UserRoleSystem/User.user):"
                    '\n  Assign the role "BR_Engineer" to the user "Anonymous". Create that user if it doesn\'t already exist, assign no password.'
                    "\n"
                    "\n- To allow access to a File device from a running mappView application, it is now required to explicitly whitelist it for reading:"
                    "\n  - Open the mappView server configuration file Configuration View/mappView/Config.mappviewcfg)"
                    '\n  - Check "Change Advanced Parameter Visibility" button in the editor toolbar'
                    '\n  - Enter your accessed File device "Name" under "MappViewConfiguration->Server configuration->File device whitelist"',
                    when="AS6",
                    severity="WARNING",
                )

    if verbose:
        # Walk through all directories

        for mappView_path in Path(directory, "Physical").rglob("mappView"):
            if mappView_path.is_dir():
                log(f"mappView folders found at: {mappView_path}", severity="INFO")
