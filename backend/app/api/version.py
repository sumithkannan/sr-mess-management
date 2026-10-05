import json
import os
import subprocess
import time
from datetime import datetime, timezone

from fastapi import APIRouter

from ..config import BASE_DIR

router = APIRouter(prefix="/api", tags=["Meta"])

PROCESS_STARTED = time.time()
STAMP_PATH = os.path.join(BASE_DIR, "deploy_stamp.json")
MAIN_PATH = os.path.join(BASE_DIR, "app", "main.py")


def _read_stamp():
    try:
        with open(STAMP_PATH, encoding="utf-8-sig") as fh:
            data = json.load(fh)
            return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def _git_commit():
    try:
        result = subprocess.run(
            ["git", "-C", BASE_DIR, "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=3,
        )
        if result.returncode == 0:
            return result.stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        pass
    return None


def _source_modified_at():
    try:
        stamp = os.path.getmtime(MAIN_PATH)
    except OSError:
        return None
    return datetime.fromtimestamp(stamp, tz=timezone.utc).isoformat(timespec="seconds")


@router.get("/version")
def version():
    """Public build metadata, used to confirm a deploy actually landed."""
    stamp = _read_stamp()
    commit = stamp.get("commit") or _git_commit()
    return {
        "commit": commit[:7] if commit else None,
        "branch": stamp.get("branch"),
        "deployed_at": stamp.get("deployed_at") or _source_modified_at(),
        "source_modified_at": _source_modified_at(),
        "uptime_seconds": round(time.time() - PROCESS_STARTED, 1),
    }