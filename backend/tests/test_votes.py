from datetime import date

def test_create_vote(client, user_headers, admin_headers):
    # Create a menu item first
    r = client.post("/api/menu-items", headers=admin_headers, json={
        "meal_type_id": 1, "item_name": "Test Food", "date": str(date.today())
    })
    item_id = r.json()["id"]
    r = client.post("/api/votes", headers=user_headers, json={
        "menu_item_id": item_id, "meal_type_id": 1, "vote_date": str(date.today())
    })
    assert r.status_code == 200

def test_duplicate_vote(client, user_headers, admin_headers):
    r = client.post("/api/menu-items", headers=admin_headers, json={
        "meal_type_id": 1, "item_name": "Dup Test", "date": str(date.today())
    })
    item_id = r.json()["id"]
    client.post("/api/votes", headers=user_headers, json={
        "menu_item_id": item_id, "meal_type_id": 1, "vote_date": str(date.today())
    })
    r = client.post("/api/votes", headers=user_headers, json={
        "menu_item_id": item_id, "meal_type_id": 1, "vote_date": str(date.today())
    })
    assert r.status_code == 400

def test_get_my_votes(client, user_headers, admin_headers):
    r = client.post("/api/menu-items", headers=admin_headers, json={
        "meal_type_id": 1, "item_name": "Vote Test", "date": str(date.today())
    })
    item_id = r.json()["id"]
    client.post("/api/votes", headers=user_headers, json={
        "menu_item_id": item_id, "meal_type_id": 1, "vote_date": str(date.today())
    })
    r = client.get(f"/api/votes/my/{date.today()}", headers=user_headers)
    assert r.status_code == 200
    assert len(r.json()) >= 1

def test_delete_vote(client, user_headers, admin_headers):
    r = client.post("/api/menu-items", headers=admin_headers, json={
        "meal_type_id": 1, "item_name": "Del Vote", "date": str(date.today())
    })
    item_id = r.json()["id"]
    r = client.post("/api/votes", headers=user_headers, json={
        "menu_item_id": item_id, "meal_type_id": 1, "vote_date": str(date.today())
    })
    vote_id = r.json()["id"]
    r = client.delete(f"/api/votes/{vote_id}", headers=user_headers)
    assert r.status_code == 200
