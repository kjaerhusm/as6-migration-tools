"""Lightweight update checker for AS6 Migration Tools.
Fetches latest GitHub release and compares with current version.
Stores ignored version in a small state file next to executable or in user config dir.
"""

from __future__ import annotations
import json
import os
import sys
import urllib.request
from pathlib import Path
from typing import Optional, Dict

GITHUB_API_LATEST = "https://api.github.com/repos/br-automation-community/as6-migration-tools/releases/latest"
STATE_FILE_NAME = "update_state.json"


def _state_path() -> Path:
    # Prefer writable dir: next to executable if possible, else user config
    base: Path
    try:
        if getattr(sys, "frozen", False):
            base = Path(sys.executable).parent
        else:
            base = Path(__file__).parent
        if os.access(base, os.W_OK):
            return base / STATE_FILE_NAME
    except Exception:
        pass
    # Fallback to user home config
    home = Path.home() / ".as6_migration_tools"
    home.mkdir(parents=True, exist_ok=True)
    return home / STATE_FILE_NAME


def load_state() -> Dict:
    p = _state_path()
    if p.is_file():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_state(state: Dict) -> None:
    p = _state_path()
    try:
        p.write_text(json.dumps(state, indent=2), encoding="utf-8")
    except Exception:
        pass  # Non-fatal


def get_ignored_version() -> Optional[str]:
    return load_state().get("ignored_version")


def set_ignored_version(version: str) -> None:
    st = load_state()
    st["ignored_version"] = version
    save_state(st)


def clear_ignored_version() -> None:
    st = load_state()
    if "ignored_version" in st:
        del st["ignored_version"]
        save_state(st)


def fetch_latest_release(timeout: float = 10.0) -> Optional[Dict]:
    req = urllib.request.Request(
        GITHUB_API_LATEST,
        headers={
            "User-Agent": "AS6-Migration-Tools-UpdateCheck",
            "Accept": "application/vnd.github+json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status != 200:
                return None
            data = json.loads(resp.read().decode("utf-8", errors="replace"))
            return data
    except Exception:
        return None


def normalize_version(v: str) -> str:
    return v.strip()


def parse_version_tuple(v: str):
    v = v.lstrip("vV")
    parts = v.split(".")
    nums = []
    for p in parts:
        try:
            nums.append(int(p))
        except ValueError:
            nums.append(-1)
    while len(nums) < 4:
        nums.append(-1)
    return tuple(nums[:4])


def is_newer(remote: str, local: str) -> bool:
    if local == "dev":
        return True  # dev always treat as older
    return parse_version_tuple(remote) > parse_version_tuple(local)


def check_for_newer(current_version: str) -> Optional[Dict]:
    """Return dict with release info if a newer (and not ignored) version exists."""
    release = fetch_latest_release()
    if not release:
        return None
    tag = release.get("tag_name") or ""
    if not tag:
        return None
    tag = normalize_version(tag)
    if tag == get_ignored_version():
        return None
    if not is_newer(tag, current_version):
        return None
    assets = release.get("assets", [])
    dl_url = None
    for a in assets:
        if a.get("name") == "as6-migration-tools.zip":
            dl_url = a.get("browser_download_url")
            break
    return {
        "tag": tag,
        "html_url": release.get("html_url"),
        "download_url": dl_url,
        "published_at": release.get("published_at"),
        "body": release.get("body") or "",
    }


__all__ = [
    "check_for_newer",
    "set_ignored_version",
    "get_ignored_version",
    "clear_ignored_version",
]
