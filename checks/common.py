import re

# Check the project name and path for invalid characters
# As opposed to what's in the help, we need to allow : and \ and / as well since these are valid
# path separators
def check_project_path_and_name(path, name, log, verbose=False):
    project_name_pattern = r"^(\w+)\.apj$"
    project_path_pattern = r"^[\w :\\/!(){}+\-@\.\^=]+$"
    if not re.fullmatch(project_path_pattern, path) or not re.fullmatch(
        project_name_pattern, name
    ):
        log(
            "Invalid path or project name, see "
            "https://help.br-automation.com/#/en/6/revinfos/version-info/projekt_aus_automation_studio_4_ubernehmen/automation_studio/notwendige_anpassungen_im_automation_studio_4_projekt.html",
            severity="ERROR",
        )
