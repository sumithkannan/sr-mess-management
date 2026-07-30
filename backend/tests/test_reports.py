from datetime import date, timedelta

def test_vote_vs_attendance_report(client, admin_headers):
    today = date.today()
    r = client.get(f"/api/reports/vote-vs-attendance?date_from={today}&date_to={today}", headers=admin_headers)
    assert r.status_code == 200

def test_meal_summary_report(client, admin_headers):
    today = date.today()
    r = client.get(f"/api/reports/meal-summary?date_from={today}&date_to={today}", headers=admin_headers)
    assert r.status_code == 200

def test_ratings_summary_report(client, admin_headers):
    today = date.today()
    r = client.get(f"/api/reports/ratings-summary?date_from={today}&date_to={today}", headers=admin_headers)
    assert r.status_code == 200

def test_export_pdf(client, admin_headers):
    today = date.today()
    r = client.get(f"/api/reports/export-pdf?report_type=vote_vs_attendance&date_from={today}&date_to={today}",
                   headers=admin_headers)
    assert r.status_code == 200
    assert r.headers.get("content-type") == "application/pdf"

def test_invalid_report_type(client, admin_headers):
    today = date.today()
    r = client.get(f"/api/reports/export-pdf?report_type=invalid&date_from={today}&date_to={today}",
                   headers=admin_headers)
    assert r.status_code == 400

def test_reports_forbidden(client, user_headers):
    today = date.today()
    r = client.get(f"/api/reports/vote-vs-attendance?date_from={today}&date_to={today}", headers=user_headers)
    assert r.status_code == 403
