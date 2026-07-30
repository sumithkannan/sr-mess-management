from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import date
from ..dependencies import get_db, get_current_user, admin_required
from ..models.off_day import OffDay
from ..schemas.off_day import OffDayCreate, OffDayResponse

router = APIRouter(prefix="/api/off-days", tags=["Off Days"])

@router.get("", response_model=list[OffDayResponse])
def list_off_days(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(OffDay).order_by(OffDay.start_date).all()

@router.get("/check/{check_date}")
def check_off_day(check_date: date, db: Session = Depends(get_db), user=Depends(get_current_user)):
    off = db.query(OffDay).filter(
        OffDay.start_date <= check_date,
        OffDay.end_date >= check_date
    ).first()
    if off:
        return {"is_off": True, "id": off.id, "reason": off.reason,
                "start_date": off.start_date, "end_date": off.end_date}
    return {"is_off": False}

@router.post("", response_model=OffDayResponse)
def create_off_day(req: OffDayCreate, db: Session = Depends(get_db),
                   admin=Depends(admin_required)):
    if req.start_date > req.end_date:
        raise HTTPException(400, "start_date must not be after end_date")
    off = OffDay(start_date=req.start_date, end_date=req.end_date,
                 reason=req.reason, created_by=admin.id)
    db.add(off); db.commit(); db.refresh(off)
    return off

@router.delete("/{off_id}")
def delete_off_day(off_id: int, db: Session = Depends(get_db),
                   admin=Depends(admin_required)):
    off = db.query(OffDay).filter(OffDay.id == off_id).first()
    if not off:
        raise HTTPException(404, "Off day not found")
    db.delete(off); db.commit()
    return {"detail": "Deleted"}
