"""Install requirements.txt automatically when the PythonAnywhere web app starts.

PythonAnywhere's API cannot start a console headlessly (``send_input`` returns
412 until the console has been opened in a browser), so CI cannot run ``pip``
directly. Instead the web app installs changed requirements on startup —
``app.main`` calls :func:`ensure_dependencies` before importing third-party
packages, so it runs whatever the WSGI entry point is — and records the result
in ``deploy_dependencies.json``; the "Install backend dependencies" GitHub
workflow reloads the site and waits for that file.

Free PythonAnywhere accounts have no direct outbound internet from web-app
workers, so pip reaches PyPI through the platform proxy
(``http://proxy.server:3128``). Paid accounts have direct access, so the
installer tries the proxy first and falls back to a direct connection.

This module must only use the standard library, because it runs before the
application (and its dependencies) is imported.
"""

import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REQUIREMENTS_PATH = os.path.join(BASE_DIR, "requirements.txt")
STATUS_PATH = os.path.join(BASE_DIR, "deploy_dependencies.json")
LOCK_PATH = os.path.join(BASE_DIR, ".deploy_dependencies.lock")
STAMP_PATH = os.path.join(BASE_DIR, "deploy_stamp.json")
PROXY_URL = "http://proxy.server:3128"
TIMEOUT_SECONDS = 300
PROXY_ENV_VARS = (
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "ALL_PROXY",
    "http_proxy",
    "https_proxy",
    "all_proxy",
)


def is_deployed_environment() -> bool:
    """True when this checkout is a live deployment that may install packages.

    PythonAnywhere sets PYTHONANYWHERE_DOMAIN / PYTHONANYWHERE_SITE for
    consoles, but not reliably for web-app workers, so do not depend on them
    alone. The deploy workflow writes ``deploy_stamp.json`` next to
    ``requirements.txt`` on every deploy; its presence marks a deployed
    checkout. Requiring Linux keeps local Windows/macOS checkouts from ever
    running pip, even if such a file is left behind.
    """
    if os.environ.get("PYTHONANYWHERE_DOMAIN") or os.environ.get("PYTHONANYWHERE_SITE"):
        return True
    return sys.platform.startswith("linux") and os.path.isfile(STAMP_PATH)


def _sha256(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def _read_status() -> dict:
    try:
        with open(STATUS_PATH, encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def _write_status(status: dict) -> None:
    tmp_path = STATUS_PATH + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as fh:
        json.dump(status, fh, indent=2)
    os.replace(tmp_path, STATUS_PATH)


def _log(message: str) -> None:
    print(f"[dependencies] {message}", file=sys.stderr, flush=True)


def _is_installed(digest: str) -> bool:
    status = _read_status()
    return status.get("status") == "ok" and status.get("requirements_sha256") == digest


def pip_environment(proxy: str | None) -> dict:
    """Environment for a pip run.

    Any proxy inherited from the platform is dropped so the two attempts are
    truly different: ``proxy`` (free accounts) and direct (paid accounts).
    """
    env = os.environ.copy()
    for name in PROXY_ENV_VARS:
        env.pop(name, None)
    if proxy:
        for name in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"):
            env[name] = proxy
    return env


def run_pip(proxy: str | None) -> tuple[int, str]:
    """Run pip once, through ``proxy`` when given. Returns (returncode, output)."""
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            "--retries",
            "2",
            "--timeout",
            "30",
            "-r",
            REQUIREMENTS_PATH,
        ],
        capture_output=True,
        text=True,
        timeout=TIMEOUT_SECONDS,
        env=pip_environment(proxy),
    )
    output = (result.stdout or "") + (result.stderr or "")
    return result.returncode, output


def ensure_dependencies() -> None:
    if not is_deployed_environment() or not os.path.isfile(REQUIREMENTS_PATH):
        return

    digest = _sha256(REQUIREMENTS_PATH)
    if _is_installed(digest):
        return

    lock = None
    try:
        import fcntl

        lock = open(LOCK_PATH, "w")
        fcntl.flock(lock, fcntl.LOCK_EX)
    except (ImportError, OSError):
        # Non-POSIX platform or unwritable directory: proceed without a lock.
        lock = None

    try:
        # Another worker may have installed the requirements while we waited.
        if _is_installed(digest):
            return

        _log(f"installing {REQUIREMENTS_PATH}")
        # Record that an install is in progress. If the worker is killed
        # mid-pip the next startup sees a non-"ok" status and retries; the
        # workflow can also tell "never started" from "still running".
        _write_status({
            "requirements_sha256": digest,
            "status": "installing",
            "started_at": datetime.now(timezone.utc).isoformat(),
        })

        # Free accounts reach PyPI only through the platform proxy; paid
        # accounts have direct access. Try the proxy first and fall back.
        attempts = (("proxy", PROXY_URL), ("direct", None))
        returncode = -1
        output = ""
        used = None
        logs = []
        for label, proxy in attempts:
            _log(f"running pip via {label}")
            try:
                returncode, output = run_pip(proxy)
            except Exception as exc:  # timeout, missing pip, ...
                returncode = -1
                output = f"{type(exc).__name__}: {exc}"
            logs.append(f"--- pip via {label} (exit {returncode}) ---\n{output}")
            if returncode == 0:
                used = label
                break
            _log(f"pip via {label} failed with exit code {returncode}")

        _write_status({
            "requirements_sha256": digest,
            "status": "ok" if returncode == 0 else "error",
            "returncode": returncode,
            "attempt": used or "none",
            "installed_at": datetime.now(timezone.utc).isoformat(),
            "output": "\n".join(logs)[-6000:],
        })
        if returncode == 0:
            _log(f"requirements installed via {used}")
        else:
            _log(f"pip failed with exit code {returncode}; see {STATUS_PATH}")
    finally:
        if lock is not None:
            try:
                import fcntl

                fcntl.flock(lock, fcntl.LOCK_UN)
            finally:
                lock.close()


if __name__ == "__main__":
    ensure_dependencies()
