def test_get_public_config(client):
    r = client.get("/api/config")
    assert r.status_code == 200

def test_update_config(client, admin_headers):
    r = client.put("/api/config", headers=admin_headers, json={
        "key": "mess_name", "value": "SR Mess"
    })
    assert r.status_code == 200

def test_get_all_config(client, admin_headers):
    client.put("/api/config", headers=admin_headers, json={
        "key": "mess_name", "value": "Test Mess"
    })
    r = client.get("/api/config/all", headers=admin_headers)
    assert r.status_code == 200
    assert len(r.json()) >= 1

def test_config_forbidden(client, user_headers):
    r = client.get("/api/config/all", headers=user_headers)
    assert r.status_code == 403
