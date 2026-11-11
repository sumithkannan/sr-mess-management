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
    monkeypatch.setattr(dd, "is_deployed_environment", lambda: False)

    def fail(*args, **kwargs):
        raise AssertionError("pip must not run outside PythonAnywhere")

    monkeypatch.setattr(dd.subprocess, "run", fail)
    dd.ensure_dependencies()


def test_installs_changed_requirements(tmp_path, monkeypatch):
    requirements, status_path = _setup_paths(tmp_path, monkeypatch)
    monkeypatch.setattr(dd, "is_deployed_environment", lambda: True)
    monkeypatch.setattr(dd.subprocess, "run", lambda *a, **k: FakeResult(0, "Successfully installed"))

    dd.ensure_dependencies()

    status = json.loads(status_path.read_text())
    assert status["status"] == "ok"
    assert status["requirements_sha256"] == dd._sha256(str(requirements))


def test_skips_when_hash_already_installed(tmp_path, monkeypatch):
    requirements, _ = _setup_paths(tmp_path, monkeypatch)
    monkeypatch.setattr(dd, "is_deployed_environment", lambda: True)
    dd._write_status({
        "status": "ok",
        "requirements_sha256": dd._sha256(str(requirements)),
    })

    def fail(*args, **kwargs):
        raise AssertionError("pip must not run when requirements are unchanged")

    monkeypatch.setattr(dd.subprocess, "run", fail)
    dd.ensure_dependencies()


def test_marks_status_installing_while_pip_runs(tmp_path, monkeypatch):
    _, status_path = _setup_paths(tmp_path, monkeypatch)
    monkeypatch.setattr(dd, "is_deployed_environment", lambda: True)
    seen = {}

    def fake_run(*args, **kwargs):
        seen.update(json.loads(status_path.read_text()))
        return FakeResult(0)

    monkeypatch.setattr(dd.subprocess, "run", fake_run)
    dd.ensure_dependencies()

    assert seen["status"] == "installing"
    assert json.loads(status_path.read_text())["status"] == "ok"


def test_records_pip_failure(tmp_path, monkeypatch):
    _, status_path = _setup_paths(tmp_path, monkeypatch)
    monkeypatch.setattr(dd, "is_deployed_environment", lambda: True)
    monkeypatch.setattr(dd.subprocess, "run", lambda *a, **k: FakeResult(1, "", "boom"))

    dd.ensure_dependencies()

    status = json.loads(status_path.read_text())
    assert status["status"] == "error"
    assert status["returncode"] == 1
    assert "boom" in status["output"]


def test_detects_deployed_checkout_from_stamp(tmp_path, monkeypatch):
    monkeypatch.delenv("PYTHONANYWHERE_DOMAIN", raising=False)
    monkeypatch.delenv("PYTHONANYWHERE_SITE", raising=False)
    stamp = tmp_path / "deploy_stamp.json"
    stamp.write_text("{}")
    monkeypatch.setattr(dd, "STAMP_PATH", str(stamp))
    monkeypatch.setattr(dd.sys, "platform", "linux")

    assert dd.is_deployed_environment() is True


def test_ignores_stamp_outside_linux(tmp_path, monkeypatch):
    monkeypatch.delenv("PYTHONANYWHERE_DOMAIN", raising=False)
    monkeypatch.delenv("PYTHONANYWHERE_SITE", raising=False)
    stamp = tmp_path / "deploy_stamp.json"
    stamp.write_text("{}")
    monkeypatch.setattr(dd, "STAMP_PATH", str(stamp))
    monkeypatch.setattr(dd.sys, "platform", "win32")

    assert dd.is_deployed_environment() is False


def test_detects_pythonanywhere_environment(monkeypatch):
    monkeypatch.setenv("PYTHONANYWHERE_SITE", "www.pythonanywhere.com")

    assert dd.is_deployed_environment() is True


def test_pip_environment_injects_and_clears_proxy(monkeypatch):
    monkeypatch.setenv("HTTPS_PROXY", "http://inherited.example:8080")
    monkeypatch.setenv("CUSTOM_SETTING", "keep-me")

    proxied = dd.pip_environment(dd.PROXY_URL)
    assert proxied["HTTPS_PROXY"] == dd.PROXY_URL
    assert proxied["HTTP_PROXY"] == dd.PROXY_URL
    assert proxied["https_proxy"] == dd.PROXY_URL
    assert proxied["http_proxy"] == dd.PROXY_URL
    # Unrelated variables are preserved.
    assert proxied["CUSTOM_SETTING"] == "keep-me"

    direct = dd.pip_environment(None)
    for name in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"):
        assert name not in direct


def test_installs_through_proxy_first(tmp_path, monkeypatch):
    _, status_path = _setup_paths(tmp_path, monkeypatch)
    monkeypatch.setattr(dd, "is_deployed_environment", lambda: True)
    envs = []

    def fake_run(args, **kwargs):
        envs.append(kwargs["env"])
        return FakeResult(0)

    monkeypatch.setattr(dd.subprocess, "run", fake_run)
    dd.ensure_dependencies()

    assert len(envs) == 1, "a successful proxy attempt must not fall back"
    assert envs[0]["HTTPS_PROXY"] == dd.PROXY_URL
    status = json.loads(status_path.read_text())
    assert status["status"] == "ok"
    assert status["attempt"] == "proxy"


def test_falls_back_to_direct_when_proxy_fails(tmp_path, monkeypatch):
    _, status_path = _setup_paths(tmp_path, monkeypatch)
    monkeypatch.setattr(dd, "is_deployed_environment", lambda: True)
    envs = []

    def fake_run(args, **kwargs):
        envs.append(kwargs["env"])
        return FakeResult(0) if len(envs) == 2 else FakeResult(1, "", "proxy unreachable")

    monkeypatch.setattr(dd.subprocess, "run", fake_run)
    dd.ensure_dependencies()

    assert len(envs) == 2
    assert envs[0]["HTTPS_PROXY"] == dd.PROXY_URL
    assert "HTTPS_PROXY" not in envs[1]
    status = json.loads(status_path.read_text())
    assert status["status"] == "ok"
    assert status["attempt"] == "direct"
    # Both attempts are kept for troubleshooting.
    assert "proxy unreachable" in status["output"]


def test_records_both_attempts_when_all_fail(tmp_path, monkeypatch):
    _, status_path = _setup_paths(tmp_path, monkeypatch)
    monkeypatch.setattr(dd, "is_deployed_environment", lambda: True)
    monkeypatch.setattr(dd.subprocess, "run", lambda *a, **k: FakeResult(1, "", "no route"))

    dd.ensure_dependencies()

    status = json.loads(status_path.read_text())
    assert status["status"] == "error"
    assert status["attempt"] == "none"
    assert "pip via proxy" in status["output"]
    assert "pip via direct" in status["output"]
