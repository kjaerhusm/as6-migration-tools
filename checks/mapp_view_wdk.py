"""
Detect legacy mappView WDK (Widget Development Kit) usage.

Rule of thumb:
- Under the project's Logical tree, look for any 'mappView/Widgets' folder.
- If ANY folder at or below that Widgets root contains BOTH a '.js' file and a '.html' file
  in the same folder, the project is considered to be using WDK.
- As soon as we find the first such folder, we stop scanning (performance).

Action:
- Emit a MANDATORY AS6 warning with guidance to migrate to WDTC (Widget Development Tool Chain)
  and provide a link to the B&R community.
"""

import os
from pathlib import Path
from typing import Iterator, Optional


def _find_widgets_roots(logical_path: Path) -> Iterator[Path]:
    """
    Yield all 'Widgets' directories under any 'mappView' folder in the Logical tree.
    """
    if not logical_path or not logical_path.exists():
        return
    # Search for 'mappView' folders anywhere below Logical, then append 'Widgets'
    for mv in logical_path.rglob("mappView"):
        widgets = mv / "Widgets"
        if widgets.is_dir():
            yield widgets


def _find_first_wdk_folder(widgets_root: Path) -> Optional[Path]:
    """
    Return the first folder (any depth under the given Widgets root, including the root)
    that contains BOTH a .js and a .html file. If none found, return None.
    Uses os.walk to avoid repeated directory listings.
    """
    for folder, _dirs, files in os.walk(widgets_root):
        if not files:
            continue
        has_js = any(name.lower().endswith(".js") for name in files)
        has_html = any(name.lower().endswith(".html") for name in files)
        if has_js and has_html:
            return Path(folder)
    return None


def check_wdk_usage(logical_path: Path, log, verbose: bool = False) -> None:
    """
    Detect usage of the legacy mappView *WDK* (Widget Development Kit) and warn that it
    must be migrated to *WDTC* (Widget Development Tool Chain) in AS6.

    Detection:
    - Look for a 'Widgets' folder under any 'mappView' directory inside the project's 'Logical' tree.
    - If any folder under that 'Widgets' root (including itself) contains BOTH a '.js' file and a '.html' file
      in the same folder, the project is considered to be using WDK.
    - Stop scanning after the first hit (we only need to know that WDK is used).

    Logging:
    - Severity: MANDATORY
    - Scope: AS6
    - Include a community link for WDTC migration info.
    - Log one example path to a detected folder (there may be more).
    """
    if verbose:
        log("Checking for legacy mappView WDK usage...")

    widgets_roots = list(_find_widgets_roots(logical_path))
    if not widgets_roots:
        if verbose:
            log("No 'mappView/Widgets' folders found under Logical.", severity="INFO")
        return

    example_hit: Optional[Path] = None
    for root in widgets_roots:
        example_hit = _find_first_wdk_folder(root)
        if example_hit:
            break

    if example_hit:
        try:
            rel = example_hit.relative_to(logical_path)
        except Exception:
            rel = example_hit
        log(
            "WDK (Widget Development Kit) detected - it is deprecated and no longer supported in AS6."
            "\n - In AS6, you must migrate to WDTC (Widget Development Tool Chain)."
            "\n - For more information, visit the B&R Community: https://community.br-automation.com/c/wdtc/10"
            f"\n - Example WDK-like widget folder (one or more may exist): {rel}",
            when="AS6",
            severity="MANDATORY",
        )

    else:
        if verbose:
            log("No WDK usage detected in mappView/Widgets.", severity="INFO")
