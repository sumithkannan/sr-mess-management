def test_list_users(client, admin_headers):
    r = client.get("/api/users", headers=admin_headers)
    assert r.status_code == 200
    assert len(r.json()) >= 3

def test_list_users_forbidden(client, user_headers):
    r = client.get("/api/users", headers=user_headers)
    assert r.status_code == 403

def test_create_user(client, admin_headers):
    r = client.post("/api/users", headers=admin_headers, json={
        "username": "newuser", "name": "New User", "email": "new@test.com"
    })
    assert r.status_code == 200
    assert r.json()["username"] == "newuser"

def test_create_duplicate_username(client, admin_headers):
    r = client.post("/api/users", headers=admin_headers, json={
        "username": "user1", "name": "Dup"
    })
    assert r.status_code == 400

def test_suspend_user(client, admin_headers):
    r = client.patch("/api/users/2/suspend", headers=admin_headers)
    assert r.status_code == 200

def test_activate_user(client, admin_headers):
    client.patch("/api/users/2/suspend", headers=admin_headers)
    r = client.patch("/api/users/2/activate", headers=admin_headers)
    assert r.status_code == 200

def test_promote_user(client, admin_headers):
    r = client.patch("/api/users/2/role?role=admin", headers=admin_headers)
    assert r.status_code == 200

def test_delete_user(client, admin_headers):
    r = client.delete("/api/users/3", headers=admin_headers)
    assert r.status_code == 200

def test_delete_nonexistent(client, admin_headers):
    r = client.delete("/api/users/999", headers=admin_headers)
    assert r.status_code == 404
