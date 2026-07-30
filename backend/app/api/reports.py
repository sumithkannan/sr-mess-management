from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import date
from ..dependencies import get_db, admin_required
from ..services.pdf_service import generate_pdf_report

router = APIRouter(prefix="/api/reports", tags=["Reports"])

@router.get("/vote-vs-attendance")
def vote_vs_attendance(date_from: date, date_to: date, meal_type_id: int = None,
                       db: Session = Depends(get_db), admin=Depends(admin_required)):
    query = """
    SELECT u.id, u.name,
           CASE WHEN v.id IS NOT NULL THEN 1 ELSE 0 END as voted,
           CASE WHEN a.id IS NOT NULL THEN 1 ELSE 0 END as ate
    FROM users u
    LEFT JOIN votes v ON v.user_id = u.id AND v.vote_date BETWEEN :dfrom AND :dto
    LEFT JOIN attendance a ON a.user_id = u.id AND a.date BETWEEN :dfrom AND :dto
    WHERE u.is_active = 1
    """
    params = {"dfrom": date_from, "dto": date_to}
    if meal_type_id:
        query += " AND (v.meal_type_id = :mt OR v.meal_type_id IS NULL)"
        query += " AND (a.meal_type_id = :mt OR a.meal_type_id IS NULL)"
        params["mt"] = meal_type_id
    query += " ORDER BY u.name"
    result = db.execute(text(query), params)
    rows = [{"id": r[0], "name": r[1], "voted": bool(r[2]), "ate": bool(r[3])} for r in result]
    return rows

@router.get("/meal-summary")
def meal_summary(date_from: date, date_to: date, db: Session = Depends(get_db),
                 admin=Depends(admin_required)):
    query = """
    SELECT mt.name as meal_type, v.vote_date, COUNT(DISTINCT v.id) as votes,
           COUNT(DISTINCT a.id) as served
    FROM meal_types mt
    LEFT JOIN votes v ON v.meal_type_id = mt.id AND v.vote_date BETWEEN :dfrom AND :dto
    LEFT JOIN attendance a ON a.meal_type_id = mt.id AND a.date BETWEEN :dfrom AND :dto
    GROUP BY mt.id, v.vote_date
    ORDER BY mt.sort_order, v.vote_date
    """
    result = db.execute(text(query), {"dfrom": date_from, "dto": date_to})
    rows = []
    for r in result:
        rows.append({
            "meal_type": r[0], "date": str(r[1]) if r[1] else None,
            "votes": r[2] or 0, "served": r[3] or 0
        })
    return rows

@router.get("/ratings-summary")
def ratings_summary(date_from: date, date_to: date, db: Session = Depends(get_db),
                    admin=Depends(admin_required)):
    query = """
    SELECT mt.name, r.date, COUNT(r.id), AVG(r.rating)
    FROM ratings r
    JOIN meal_types mt ON mt.id = r.meal_type_id
    WHERE r.date BETWEEN :dfrom AND :dto
    GROUP BY mt.id, r.date
    ORDER BY mt.sort_order, r.date
    """
    result = db.execute(text(query), {"dfrom": date_from, "dto": date_to})
    rows = []
    for r in result:
        rows.append({
            "meal_type": r[0], "date": str(r[1]) if r[1] else None,
            "count": r[2], "avg_rating": round(float(r[3]), 2) if r[3] else 0
        })
    return rows

@router.get("/user-report/{user_id}")
def user_report(user_id: int, date_from: date, date_to: date,
                db: Session = Depends(get_db), admin=Depends(admin_required)):
    from ..models.user import User
    user = db.query(User).filter(User.id == user_id).first()
    if not user: raise HTTPException(status_code=404)
    query = """
    SELECT v.vote_date, mt.name,
           CASE WHEN a.id IS NOT NULL THEN 1 ELSE 0 END as ate
    FROM votes v
    JOIN meal_types mt ON mt.id = v.meal_type_id
    LEFT JOIN attendance a ON a.user_id = v.user_id AND a.meal_type_id = v.meal_type_id AND a.date = v.vote_date
    WHERE v.user_id = :uid AND v.vote_date BETWEEN :dfrom AND :dto
    ORDER BY v.vote_date
    """
    result = db.execute(text(query), {"uid": user_id, "dfrom": date_from, "dto": date_to})
    records = [{"date": str(r[0]), "meal_type": r[1], "ate": bool(r[2])} for r in result]
    return {"user": {"id": user.id, "name": user.name}, "records": records}

@router.get("/export-pdf")
def export_pdf(report_type: str, date_from: date, date_to: date,
               meal_type_id: int = None, user_id: int = None,
               db: Session = Depends(get_db), admin=Depends(admin_required)):
    title = f"{report_type.replace('_', ' ').title()} ({date_from} to {date_to})"
    data = []
    headers = []
    rows = []

    if report_type == "vote_vs_attendance":
        data = vote_vs_attendance(date_from, date_to, meal_type_id, db, admin)
        headers = ["Name", "Voted", "Ate"]
        rows = [[d["name"], "Yes" if d["voted"] else "No", "Yes" if d["ate"] else "No"] for d in data]
    elif report_type == "meal_summary":
        data = meal_summary(date_from, date_to, db, admin)
        headers = ["Meal Type", "Date", "Votes", "Served"]
        rows = [[d["meal_type"], d["date"], d["votes"], d["served"]] for d in data]
    elif report_type == "ratings_summary":
        data = ratings_summary(date_from, date_to, db, admin)
        headers = ["Meal Type", "Date", "Count", "Avg Rating"]
        rows = [[d["meal_type"], d["date"], d["count"], d["avg_rating"]] for d in data]
    elif report_type == "user_report" and user_id:
        data = user_report(user_id, date_from, date_to, db, admin)
        title = f"User Report: {data['user']['name']} ({date_from} to {date_to})"
        headers = ["Date", "Meal Type", "Ate"]
        rows = [[d["date"], d["meal_type"], "Yes" if d["ate"] else "No"] for d in data["records"]]
    else:
        raise HTTPException(status_code=400, detail="Invalid report type")

    pdf_bytes = generate_pdf_report(title, headers, rows)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={report_type}.pdf"}
    )
