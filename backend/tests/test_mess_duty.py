from datetime import date, timedelta

def test_assign_mess_duty(client, admin_headers):
    today = date.today()
    r = client.post("/api/mess-duty", headers=admin_headers, json={
        "user_id": 2, "start_date": str(today), "end_date": str(today + timedelta(days=7))
    })
    assert r.status_code == 200
    assert r.json()["user_id"] == 2

def test_get_current_duty(client, admin_headers):
    today = date.today()
    client.post("/api/mess-duty", headers=admin_headers, json={
        "user_id": 2, "start_date": str(today), "end_date": str(today + timedelta(days=7))
    })
    r = client.get("/api/mess-duty/current")
    assert r.status_code == 200
    assert len(r.json()) >= 1

def test_list_assignments(client, admin_headers):
    r = client.get("/api/mess-duty", headers=admin_headers)
    assert r.status_code == 200

def test_remove_assignment(client, admin_headers):
    today = date.today()
    r = client.post("/api/mess-duty", headers=admin_headers, json={
        "user_id": 2, "start_date": str(today), "end_date": str(today + timedelta(days=7))
    })
    duty_id = r.json()["id"]
    r = client.delete(f"/api/mess-duty/{duty_id}", headers=admin_headers)
    assert r.status_code == 200
