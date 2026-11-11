import json

import deploy_dependencies as dd


class FakeResult:
    def __init__(self, returncode, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def _setup_paths(tmp_path, monkeypatch):
    requirements = tmp_path / "requirements.txt"
    requirements.write_text("fastapi==0.115.4\n")
    monkeypatch.setattr(dd, "REQUIREMENTS_PATH", str(requirements))
    monkeypatch.setattr(dd, "STATUS_PATH", str(tmp_path / "status.json"))
    monkeypatch.setattr(dd, "LOCK_PATH", str(tmp_path / "lock"))
    return requirements, tmp_path / "status.json"


def test_does_nothing_outside_pythonanywhere(tmp_path, monkeypatch):
    _setup_paths(tmp_path, monkeypatch)
    monkeypatch.setattr(dd, "running_on_pythonanywhere", lambda: False)

    def fail(*args, **kwargs):
        raise AssertionError("pip must not run outside PythonAnywhere")

    monkeypatch.setattr(dd.subprocess, "run", fail)
    dd.ensure_dependencies()


def test_installs_changed_requirements(tmp_path, monkeypatch):
    requirements, status_path = _setup_paths(tmp_path, monkeypatch)
    monkeypatch.setattr(dd, "running_on_pythonanywhere", lambda: True)
    monkeypatch.setattr(dd.subprocess, "run", lambda *a, **k: FakeResult(0, "Successfully installed"))

    dd.ensure_dependencies()

    status = json.loads(status_path.read_text())
    assert status["status"] == "ok"
    assert status["requirements_sha256"] == dd._sha256(str(requirements))


def test_skips_when_hash_already_installed(tmp_path, monkeypatch):
    requirements, _ = _setup_paths(tmp_path, monkeypatch)
    monkeypatch.setattr(dd, "running_on_pythonanywhere", lambda: True)
    dd._write_status({
        "status": "ok",
        "requirements_sha256": dd._sha256(str(requirements)),
    })

    def fail(*args, **kwargs):
        raise AssertionError("pip must not run when requirements are unchanged")

    monkeypatch.setattr(dd.subprocess, "run", fail)
    dd.ensure_dependencies()


def test_records_pip_failure(tmp_path, monkeypatch):
    _, status_path = _setup_paths(tmp_path, monkeypatch)
    monkeypatch.setattr(dd, "running_on_pythonanywhere", lambda: True)
    monkeypatch.setattr(dd.subprocess, "run", lambda *a, **k: FakeResult(1, "", "boom"))

    dd.ensure_dependencies()

    status = json.loads(status_path.read_text())
    assert status["status"] == "error"
    assert status["returncode"] == 1
    assert "boom" in status["output"]
