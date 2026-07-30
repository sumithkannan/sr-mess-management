from datetime import date

def test_create_expense(client, admin_headers):
    r = client.post("/api/expenses", headers=admin_headers, json={
        "description": "Rice 25kg", "amount": 1500, "category": "Grocery", "expense_date": str(date.today())
    })
    assert r.status_code == 200
    assert r.json()["description"] == "Rice 25kg"

def test_list_expenses(client, admin_headers):
    client.post("/api/expenses", headers=admin_headers, json={
        "description": "Vegetables", "amount": 500, "category": "Grocery", "expense_date": str(date.today())
    })
    r = client.get("/api/expenses", headers=admin_headers)
    assert r.status_code == 200
    assert len(r.json()) >= 1

def test_monthly_summary(client, admin_headers):
    client.post("/api/expenses", headers=admin_headers, json={
        "description": "Test", "amount": 100, "category": "Other", "expense_date": str(date.today())
    })
    r = client.get(f"/api/expenses/monthly-summary?month={date.today().month}&year={date.today().year}",
                   headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["total_entries"] >= 1

def test_update_expense(client, admin_headers):
    r = client.post("/api/expenses", headers=admin_headers, json={
        "description": "Milk", "amount": 200, "category": "Grocery", "expense_date": str(date.today())
    })
    exp_id = r.json()["id"]
    r = client.put(f"/api/expenses/{exp_id}", headers=admin_headers, json={"amount": 250})
    assert r.status_code == 200
    assert float(r.json()["amount"]) == 250

def test_delete_expense(client, admin_headers):
    r = client.post("/api/expenses", headers=admin_headers, json={
        "description": "Temp", "amount": 50, "category": "Other", "expense_date": str(date.today())
    })
    exp_id = r.json()["id"]
    r = client.delete(f"/api/expenses/{exp_id}", headers=admin_headers)
    assert r.status_code == 200
