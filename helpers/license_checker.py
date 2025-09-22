import os
import sys
from pathlib import Path
from checks import mapp_analyser as ma

from utils import utils


def get_amount(cnt):
    return f"{cnt} {'time' if cnt == 1 else 'times'}"


def main():
    project_path = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    apj_file = utils.get_and_check_project_file(project_path)

    utils.log(f"Project path validated: {project_path}")
    utils.log(f"Using project file: {apj_file}\n")

    utils.log(
        "This script will check which mapp licenses are need in the project",
        severity="INFO",
    )

    supported_services = [
        "mappView",
        "mappConnect",
        "mappTrak",
        "mappServices",
        "mappVision",
    ]
    status = "Currently the following mapp technologies are supported:"
    for service in supported_services:
        status += f"\n - {service}"
    utils.log(
        status,
        severity="INFO",
    )

    analyse = ma.mapp_license_analyser(Path(project_path))

    # reporting is done here
    totalLicenses = []
    if analyse["mappView"] is not None:
        utils.log(
            "mappView licenses",
            severity="INFO",
        )
        premiumWidgetCnt = 0

        for obj in analyse["mappView"]["breaseWidgets"]:
            if obj["cnt"] > 0 and obj["license"] > 0:
                premiumWidgetCnt += 1

        if premiumWidgetCnt > 0:
            status = f"License {utils.url('1TCMPVIEWWGT.10-01')} is needed due to:"
            for obj in analyse["mappView"]["breaseWidgets"]:
                if obj["cnt"] > 0 and obj["license"] > 0:
                    status += (
                        f"\n - {utils.url(f'widgets.brease.{obj["name"]}')} used "
                        f"{get_amount(obj['cnt'])}\n"
                    )

            utils.log(
                status,
                severity="MANDATORY",
            )
            totalLicenses.append("1TCMPVIEWWGT.10-01")

        if analyse["mappView"]["clientCnt"] > 1:
            utils.log(
                f"License {utils.url('1TCMPVIEWCLT.10-01')} is needed due to:\n"
                f" - {utils.url('MaxClientConnections')} is configured to "
                f"more than once ({analyse['mappView']['clientCnt']})",
                severity="MANDATORY",
            )
            totalLicenses.append("1TCMPVIEWCLT.10-01")

        if analyse["mappView"]["uaServerCnt"] > 1:
            utils.log(
                f"License {utils.url('1TCMPVIEWSRV.10-01')} is needed:\n"
                f" - {utils.url('OpcUaServerConnections')} is configured to "
                f"more than once ({get_amount(analyse['mappView']['uaServerCnt'])})",
                severity="MANDATORY",
            )
            totalLicenses.append("1TCMPVIEWSRV.10-01")

        if analyse["mappView"]["eventScriptCnt"] > 0:
            utils.log(
                f"License {utils.url('1TC6MPVIEWSCR.20')} is needed:\n"
                f" - {utils.url('Event scripts')} is added "
                f"{get_amount(analyse['mappView']['eventScriptCnt'])}",
                severity="MANDATORY",
            )
            totalLicenses.append("1TC6MPVIEWSCR.20")

        if (
            premiumWidgetCnt == 0
            and analyse["mappView"]["clientCnt"] == 0
            and analyse["mappView"]["uaServerCnt"] == 0
        ):
            utils.log(
                f"License {utils.url('1TCMPVIEW.00-01')} is sufficient for the project",
                severity="MANDATORY",
            )
            totalLicenses.append("1TCMPVIEW.00-01")
        else:
            utils.log(
                f"License {utils.url('1TCMPVIEW.20-01')} can be used instead of "
                f"{utils.url('1TCMPVIEWWGT.10-01')}, {utils.url('1TCMPVIEWCLT.10-01')} and "
                f"{utils.url('1TCMPVIEWSRV.10-01')}",
                severity="INFO",
            )

    if analyse["mappConnect"] is not None:
        if analyse["mappConnect"]["opcUaServerCnt"] > 0:
            utils.log(
                "mappConnect licenses",
                severity="INFO",
            )
            utils.log(
                f"License {utils.url('1TC6MPVIEWCON.20')} is needed due to:\n"
                f" - {utils.url('MappConnect OPC UA Server')} is configured to "
                f"{get_amount(analyse['mappConnect']['opcUaServerCnt'])}",
                severity="MANDATORY",
            )
            totalLicenses.append("1TC6MPVIEWCON.20")

    if analyse["mappTrak"] is not None:
        if (
            analyse["mappTrak"]["collisionAvoidance"] == "Variable"
            or analyse["mappTrak"]["collisionAvoidance"] == "AdvancedVariable"
        ):
            utils.log(
                "mappTrak licenses",
                severity="INFO",
            )
            utils.log(
                f"License {utils.url('1TCMPTRAK.20-01')} is needed due to:\n"
                f" - {utils.url('MappTrak Collision Avoidance')} is configured to "
                f"{get_amount(analyse['mappTrak']['collisionAvoidance'])}",
                severity="MANDATORY",
            )
            totalLicenses.append("1TCMPTRAK.20-01")
        elif len(analyse["mappTrak"]["hardware"]) > 0:
            utils.log(
                "mappTrak licenses",
                severity="INFO",
            )
            status = (
                f"License {utils.url('1TCMPTRAK.10-01')} is needed because the "
                "following hardware is used:"
            )
            for item in analyse["mappTrak"]["hardware"]:
                status += f"\n - {utils.url(item['module'])} x {item['cnt']}"
            utils.log(
                status,
                severity="MANDATORY",
            )
            totalLicenses.append("1TCMPTRAK.10-01")

    if analyse["mappServices"] is not None:
        addService = 0
        status = ""
        for obj in analyse["mappServices"]["services"]:
            if obj["cnt"] > 0 and obj["license"] > 0:
                addService = 1
                status += f" - {utils.url(f'mapp{obj["name"]}')} used {get_amount(obj['cnt'])}\n"
        if addService:
            utils.log(
                "mappServices licenses",
                severity="INFO",
            )
            utils.log(
                f"License {utils.url('1TCMPSERVICE.10-01')} is needed due to:\n{status}",
                severity="MANDATORY",
            )
            totalLicenses.append("1TCMPSERVICE.10-01")

    if analyse["mappMotion"] is not None:
        for obj in analyse["mappMotion"]["functions"]:
            if obj["type"] == "axis":
                if obj["cnt"] > 3:
                    utils.log(
                        f"License {utils.url('1TCMPAXIS.10-01')} is needed due to:\n{status}"
                        f" - {utils.url(obj['name'])} used {get_amount(obj['cnt'])}\n",
                        severity="MANDATORY",
                    )
                    totalLicenses.append("1TCMPAXIS.10-01")

    if analyse["mappVision"] is not None:
        addFunction = 0
        status = ""
        for obj in analyse["mappVision"]["functions"]:
            if obj["cnt"] > 0 and obj["license"] > 0:
                addFunction = 1
                status += f" - {utils.url(obj['name'])} used {get_amount(obj['cnt'])}\n"

        if addFunction:
            utils.log(
                f"License {utils.url('1TCMPVISION.10-01')} is needed due to:\n{status}",
                severity="MANDATORY",
            )
            totalLicenses.append("1TCMPVISION.10-01")

    # total licenses
    licenses = utils.load_file_info("licenses", "licenses")
    output = ""
    for item in totalLicenses:
        name = next(
            (lic[item]["name"] for lic in licenses if item in lic),
            "",
        )
        output += f"\n - {utils.url(item)} - {name}"

    utils.log(
        f"Total licenses needed: {output}",
        severity="MANDATORY",
    )


if __name__ == "__main__":
    main()
