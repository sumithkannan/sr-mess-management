from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from ..dependencies import get_db, get_current_user, mess_duty_or_admin
from ..models.attendance import Attendance
from ..models.vote import Vote
from ..models.menu import MealType
from ..schemas.attendance import AttendanceCreate, AttendanceBatchCreate, AttendanceResponse
from ..timeutils import local_now, meal_window

router = APIRouter(prefix="/api/attendance", tags=["Attendance"])

def check_attendance_open(meal_type_id: int, meal_date: date, db: Session) -> bool:
    mt = db.query(MealType).filter(MealType.id == meal_type_id).first()
    if not mt or not mt.start_time or not mt.end_time:
        return False
    buffer_hours = mt.attendance_buffer_hours if mt.attendance_buffer_hours is not None else 1
    start, end = meal_window(meal_date, mt.start_time, mt.end_time, buffer_hours)
    return start <= local_now() < end

@router.get("/date/{att_date}/{meal_type_id}", response_model=list[AttendanceResponse])
def get_attendance(att_date: date, meal_type_id: int, db: Session = Depends(get_db),
                   current_user=Depends(get_current_user)):
    return db.query(Attendance).filter(
        Attendance.date == att_date,
        Attendance.meal_type_id == meal_type_id
    ).all()

@router.post("", response_model=AttendanceResponse)
def mark_attendance(req: AttendanceCreate, db: Session = Depends(get_db),
                    current_user=Depends(mess_duty_or_admin)):
    if not check_attendance_open(req.meal_type_id, req.date, db):
        raise HTTPException(status_code=403, detail="Attendance window is closed")
    vote = db.query(Vote).filter(
        Vote.user_id == req.user_id,
        Vote.meal_type_id == req.meal_type_id,
        Vote.vote_date == req.date
    ).first()
    if not vote:
        raise HTTPException(status_code=403, detail="User has not voted for this meal")
    existing = db.query(Attendance).filter(
        Attendance.user_id == req.user_id,
        Attendance.meal_type_id == req.meal_type_id,
        Attendance.date == req.date
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already marked")
    att = Attendance(
        user_id=req.user_id, meal_type_id=req.meal_type_id,
        date=req.date, marked_by=current_user.id
    )
    db.add(att); db.commit(); db.refresh(att)
    return AttendanceResponse.model_validate(att)

@router.post("/batch")
def mark_batch_attendance(req: AttendanceBatchCreate, db: Session = Depends(get_db),
                          current_user=Depends(mess_duty_or_admin)):
    if not check_attendance_open(req.meal_type_id, req.date, db):
        raise HTTPException(status_code=403, detail="Attendance window is closed")
    count = 0
    for uid in req.user_ids:
        vote = db.query(Vote).filter(
            Vote.user_id == uid,
            Vote.meal_type_id == req.meal_type_id,
            Vote.vote_date == req.date
        ).first()
        if not vote:
            raise HTTPException(status_code=403, detail=f"User {uid} has not voted for this meal")
        existing = db.query(Attendance).filter(
            Attendance.user_id == uid,
            Attendance.meal_type_id == req.meal_type_id,
            Attendance.date == req.date
        ).first()
        if not existing:
            db.add(Attendance(
                user_id=uid, meal_type_id=req.meal_type_id,
                date=req.date, marked_by=current_user.id
            ))
            count += 1
    db.commit()
    return {"message": f"Marked {count} attendance records"}

@router.delete("/{att_id}")
def remove_attendance(att_id: int, db: Session = Depends(get_db),
                      current_user=Depends(mess_duty_or_admin)):
    att = db.query(Attendance).filter(Attendance.id == att_id).first()
    if not att: raise HTTPException(status_code=404)
    db.delete(att); db.commit()
    return {"message": "Attendance removed"}
