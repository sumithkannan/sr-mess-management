from datetime import date

def test_create_rating(client, user_headers, admin_headers):
    r = client.post("/api/menu-items", headers=admin_headers, json={
        "meal_type_id": 1, "item_name": "Rate Test", "date": str(date.today())
    })
    item_id = r.json()["id"]
    r = client.post("/api/ratings", headers=user_headers, json={
        "menu_item_id": item_id, "meal_type_id": 1, "date": str(date.today()), "rating": 5
    })
    assert r.status_code == 200
    assert r.json()["rating"] == 5

def test_invalid_rating(client, user_headers, admin_headers):
    r = client.post("/api/menu-items", headers=admin_headers, json={
        "meal_type_id": 1, "item_name": "Inv Rate", "date": str(date.today())
    })
    item_id = r.json()["id"]
    r = client.post("/api/ratings", headers=user_headers, json={
        "menu_item_id": item_id, "meal_type_id": 1, "date": str(date.today()), "rating": 6
    })
    assert r.status_code == 400

def test_update_rating(client, user_headers, admin_headers):
    r = client.post("/api/menu-items", headers=admin_headers, json={
        "meal_type_id": 1, "item_name": "Upd Rate", "date": str(date.today())
    })
    item_id = r.json()["id"]
    client.post("/api/ratings", headers=user_headers, json={
        "menu_item_id": item_id, "meal_type_id": 1, "date": str(date.today()), "rating": 3
    })
    r = client.post("/api/ratings", headers=user_headers, json={
        "menu_item_id": item_id, "meal_type_id": 1, "date": str(date.today()), "rating": 4
    })
    assert r.json()["rating"] == 4

def test_get_ratings(client, user_headers, admin_headers):
    r = client.post("/api/menu-items", headers=admin_headers, json={
        "meal_type_id": 1, "item_name": "Get Rate", "date": str(date.today())
    })
    item_id = r.json()["id"]
    client.post("/api/ratings", headers=user_headers, json={
        "menu_item_id": item_id, "meal_type_id": 1, "date": str(date.today()), "rating": 4
    })
    r = client.get(f"/api/ratings/date/{date.today()}")
    assert r.status_code == 200
    assert len(r.json()) >= 1
