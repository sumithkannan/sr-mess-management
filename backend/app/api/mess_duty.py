from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from ..dependencies import get_db, admin_required
from ..models.mess_duty import MessDutyAssignment
from ..models.user import User
from ..schemas.mess_duty import MessDutyCreate, MessDutyUpdate, MessDutyResponse

router = APIRouter(prefix="/api/mess-duty", tags=["Mess Duty"])

def _get_duty_users_for_date(target_date: date, db: Session):
    results = db.query(MessDutyAssignment).filter(
        MessDutyAssignment.start_date <= target_date,
        MessDutyAssignment.end_date >= target_date
    ).all()
    users = []
    for duty in results:
        user = db.query(User).filter(User.id == duty.user_id).first()
        if user:
            users.append({
                "id": user.id, "name": user.name,
                "start_date": str(duty.start_date),
                "end_date": str(duty.end_date)
            })
    return users

@router.get("/current")
def get_current_duty_users(db: Session = Depends(get_db)):
    return _get_duty_users_for_date(date.today(), db)

@router.get("/on-date/{target_date}")
def get_duty_users_on_date(target_date: date, db: Session = Depends(get_db)):
    return _get_duty_users_for_date(target_date, db)

@router.get("", response_model=list[MessDutyResponse])
def list_assignments(db: Session = Depends(get_db), admin=Depends(admin_required)):
    return db.query(MessDutyAssignment).all()

@router.post("", response_model=MessDutyResponse)
def create_assignment(req: MessDutyCreate, db: Session = Depends(get_db),
                      admin=Depends(admin_required)):
    assignment = MessDutyAssignment(**req.model_dump(), created_by=admin.id)
    db.add(assignment); db.commit(); db.refresh(assignment)
    return MessDutyResponse.model_validate(assignment)

@router.put("/{assignment_id}", response_model=MessDutyResponse)
def update_assignment(assignment_id: int, req: MessDutyUpdate, db: Session = Depends(get_db),
                      admin=Depends(admin_required)):
    ass = db.query(MessDutyAssignment).filter(MessDutyAssignment.id == assignment_id).first()
    if not ass: raise HTTPException(status_code=404)
    for k, v in req.model_dump(exclude_unset=True).items():
        setattr(ass, k, v)
    db.commit(); db.refresh(ass)
    return MessDutyResponse.model_validate(ass)

@router.delete("/{assignment_id}")
def delete_assignment(assignment_id: int, db: Session = Depends(get_db),
                      admin=Depends(admin_required)):
    ass = db.query(MessDutyAssignment).filter(MessDutyAssignment.id == assignment_id).first()
    if not ass: raise HTTPException(status_code=404)
    db.delete(ass); db.commit()
    return {"message": "Assignment removed"}
