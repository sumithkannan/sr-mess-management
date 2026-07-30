from datetime import date

def test_mark_attendance(client, admin_headers):
    r = client.post("/api/attendance", headers=admin_headers, json={
        "user_id": 2, "meal_type_id": 1, "date": str(date.today())
    })
    assert r.status_code == 200

def test_duplicate_attendance(client, admin_headers):
    client.post("/api/attendance", headers=admin_headers, json={
        "user_id": 2, "meal_type_id": 1, "date": str(date.today())
    })
    r = client.post("/api/attendance", headers=admin_headers, json={
        "user_id": 2, "meal_type_id": 1, "date": str(date.today())
    })
    assert r.status_code == 400

def test_batch_attendance(client, admin_headers):
    r = client.post("/api/attendance/batch", headers=admin_headers, json={
        "meal_type_id": 1, "date": str(date.today()), "user_ids": [2, 3]
    })
    assert r.status_code == 200
    assert r.json()["message"].startswith("Marked")

def test_get_attendance(client, admin_headers):
    client.post("/api/attendance", headers=admin_headers, json={
        "user_id": 2, "meal_type_id": 1, "date": str(date.today())
    })
    r = client.get(f"/api/attendance/date/{date.today()}/1", headers=admin_headers)
    assert r.status_code == 200
    assert len(r.json()) >= 1

def test_remove_attendance(client, admin_headers):
    r = client.post("/api/attendance", headers=admin_headers, json={
        "user_id": 2, "meal_type_id": 1, "date": str(date.today())
    })
    att_id = r.json()["id"]
    r = client.delete(f"/api/attendance/{att_id}", headers=admin_headers)
    assert r.status_code == 200
