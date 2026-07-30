from datetime import date

def test_list_meal_types(client):
    r = client.get("/api/meal-types")
    assert r.status_code == 200
    assert len(r.json()) >= 2

def test_create_meal_type(client, admin_headers):
    r = client.post("/api/meal-types", headers=admin_headers, json={
        "name": "Supper", "start_time": "19:00", "end_time": "20:00", "vote_cutoff_hours": 10, "vote_open_interval_days": 5, "rating_start_hours": 1, "sort_order": 5
    })
    assert r.status_code == 200
    assert r.json()["name"] == "Supper"
    assert r.json()["vote_cutoff_hours"] == 10

def test_update_meal_type(client, admin_headers):
    r = client.put("/api/meal-types/1", headers=admin_headers, json={
        "vote_cutoff_hours": 8
    })
    assert r.status_code == 200
    assert r.json()["vote_cutoff_hours"] == 8

def test_create_menu_item(client, admin_headers):
    r = client.post("/api/menu-items", headers=admin_headers, json={
        "meal_type_id": 1, "item_name": "Idli", "date": str(date.today())
    })
    assert r.status_code == 200
    assert r.json()["item_name"] == "Idli"

def test_create_recurring_menu_item(client, admin_headers):
    r = client.post("/api/menu-items", headers=admin_headers, json={
        "meal_type_id": 1, "item_name": "Pongal", "day_of_week": 0, "is_recurring": True
    })
    assert r.status_code == 200
    assert r.json()["is_recurring"] == True

def test_get_menu_by_date(client, admin_headers):
    client.post("/api/menu-items", headers=admin_headers, json={
        "meal_type_id": 1, "item_name": "Dosa", "date": str(date.today())
    })
    r = client.get(f"/api/menu-items/date/{date.today()}")
    assert r.status_code == 200
    assert len(r.json()) >= 1

def test_generate_menu_from_recurring(client, admin_headers):
    # Create recurring item for Monday (weekday 0)
    today = date.today()
    client.post("/api/menu-items", headers=admin_headers, json={
        "meal_type_id": 1, "item_name": "Weekly Special", "day_of_week": today.weekday(), "is_recurring": True
    })
    r = client.post(f"/api/menu-items/generate/{today}", headers=admin_headers)
    assert r.status_code == 200

def test_delete_menu_item(client, admin_headers):
    r = client.post("/api/menu-items", headers=admin_headers, json={
        "meal_type_id": 1, "item_name": "Temp", "date": str(date.today())
    })
    item_id = r.json()["id"]
    r = client.delete(f"/api/menu-items/{item_id}", headers=admin_headers)
    assert r.status_code == 200
