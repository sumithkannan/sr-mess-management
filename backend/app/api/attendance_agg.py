from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date

from ..dependencies import get_db, get_current_user
from ..models.user import User
from ..api import users, attendance, votes, mess_duty
from ..schemas.attendance import AttendanceResponse
from ..schemas.vote import VoteResponse

router = APIRouter(prefix="/api/attendance", tags=["Attendance"])


@router.get("/dashboard")
def get_attendance_dashboard(
    target_date: date = Query(..., alias="date"),
    meal_type_id: int = Query(..., alias="meal_type_id"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Thin aggregator over the attendance page's per-load queries."""
    active_users = users.list_active_users(db=db, current_user=current_user)
    attendance_list = attendance.get_attendance(
        att_date=target_date, meal_type_id=meal_type_id, db=db, current_user=current_user
    )
    vote_list = votes.get_votes_by_date(vote_date=target_date, db=db)
    duty = mess_duty.get_current_duty_users(db=db)

    return {
        "date": str(target_date),
        "meal_type_id": meal_type_id,
        "users": active_users,
        "attendance": [AttendanceResponse.model_validate(a) for a in attendance_list],
        "votes": [VoteResponse.model_validate(v) for v in vote_list],
        "mess_duty": duty,
    }
