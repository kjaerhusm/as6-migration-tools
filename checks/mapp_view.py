import re
import xml.etree.ElementTree as ET


def check_mappView(apj_path, log, verbose=False):
    """
    Checks for the presence of mappView settings files in the specified directory.
    """
    log("─" * 80 + "\nChecking mappView version in project file...")

    # Check for mappView line in the .apj file
    for line in apj_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if "<mappView " in line and "Version=" in line:
            match = re.search(r'Version="(\d+)\.(\d+)', line)
            if match:
                major = int(match.group(1))
                minor = int(match.group(2))
                version = f"{major}.{minor}"

                log(f"Found usage of mappView (Version: {version})", severity="INFO")
                log(
                    f"Several security settings will be enforced after the migration:"
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
                    "\n  ClientServerConfiguration->Security->Authentication->Authentication Methods->Anonymous: Enabled"
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

            # check for specific widgets
            # Namespace mappings
            ns = {
                "c": "http://www.br-automation.com/iat2015/contentDefinition/v2",
                "xsi": "http://www.w3.org/2001/XMLSchema-instance",
            }
            logical_path = apj_path.parent / "Logical"
            for content_path in logical_path.rglob("*.content"):
                tree = ET.parse(content_path)
                root_elem = tree.getroot()

                for widget in root_elem.findall(".//c:Widget", ns):
                    xsi_type = widget.attrib.get(f"{{{ns['xsi']}}}type")
                    if xsi_type in {
                        "widgets.brease.AuditList",
                        "widgets.brease.TextPad",
                        "widgets.brease.UserList",
                        "widgets.brease.MotionPad",
                    }:
                        log(
                            "Found use of AuditList, UserList, TextPad or MotionPad widgets that requires the role of BR_Engineer",
                            severity="INFO",
                        )
                        log(
                            "Check in the following (Configuration View/AccessAndSecurity/UserRoleSystem/User.user) that a user with role BR_Engineer is present"
                        )

    if verbose:
        # Walk through all directories
        physical_path = apj_path.parent / "Physical"
        for mappView_path in physical_path.rglob("mappView"):
            if mappView_path.is_dir():
                log(f"mappView folders found at: {mappView_path}", severity="INFO")
