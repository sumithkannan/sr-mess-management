def test_health_check(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_login_success(client):
    r = client.post("/api/auth/login", json={"username": "admin", "password": "PasswordToBeChanged"})
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data
    assert data["user"]["username"] == "admin"
    assert data["user"]["role"] == "admin"

def test_login_wrong_password(client):
    r = client.post("/api/auth/login", json={"username": "admin", "password": "wrong"})
    assert r.status_code == 401

def test_login_wrong_username(client):
    r = client.post("/api/auth/login", json={"username": "nonexistent", "password": "PasswordToBeChanged"})
    assert r.status_code == 401

def test_get_me(client, admin_headers):
    r = client.get("/api/auth/me", headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["username"] == "admin"

def test_get_me_unauthorized(client):
    r = client.get("/api/auth/me")
    assert r.status_code == 403
