from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
from ..dependencies import get_db, get_current_user
from ..models.vote import Vote
from ..models.menu import MealType
from ..schemas.vote import VoteCreate, VoteResponse

router = APIRouter(prefix="/api/votes", tags=["Votes"])

def get_vote_window(meal_type_id: int, meal_date: date, db: Session):
    mt = db.query(MealType).filter(MealType.id == meal_type_id).first()
    if not mt or not mt.start_time or mt.vote_cutoff_hours is None or mt.vote_open_interval_days is None:
        return None, None
    open_dt = datetime.combine(meal_date - timedelta(days=mt.vote_open_interval_days), datetime.min.time())
    deadline = datetime.combine(meal_date, mt.start_time) - timedelta(hours=mt.vote_cutoff_hours)
    return open_dt, deadline

def check_voting_open(meal_type_id: int, meal_date: date, db: Session) -> bool:
    open_dt, deadline = get_vote_window(meal_type_id, meal_date, db)
    if not open_dt or not deadline:
        return False
    now = datetime.now()
    return open_dt <= now < deadline

@router.get("/date/{vote_date}", response_model=list[VoteResponse])
def get_votes_by_date(vote_date: date, db: Session = Depends(get_db)):
    return db.query(Vote).filter(Vote.vote_date == vote_date).all()

@router.get("/my/{vote_date}", response_model=list[VoteResponse])
def get_my_votes(vote_date: date, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(Vote).filter(
        Vote.vote_date == vote_date,
        Vote.user_id == current_user.id
    ).all()

@router.post("", response_model=VoteResponse)
def create_vote(req: VoteCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if not check_voting_open(req.meal_type_id, req.vote_date, db):
        raise HTTPException(status_code=403, detail="Voting closed for this meal type")
    existing = db.query(Vote).filter(
        Vote.user_id == current_user.id,
        Vote.meal_type_id == req.meal_type_id,
        Vote.vote_date == req.vote_date
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already voted for this meal")
    vote = Vote(user_id=current_user.id, **req.model_dump())
    db.add(vote); db.commit(); db.refresh(vote)
    return VoteResponse.model_validate(vote)

@router.delete("/{vote_id}")
def delete_vote(vote_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    vote = db.query(Vote).filter(
        Vote.id == vote_id,
        Vote.user_id == current_user.id
    ).first()
    if not vote: raise HTTPException(status_code=404)
    if not check_voting_open(vote.meal_type_id, vote.vote_date, db):
        raise HTTPException(status_code=403, detail="Cannot unvote after cutoff")
    db.delete(vote); db.commit()
    return {"message": "Vote removed"}
