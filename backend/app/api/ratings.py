from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
from ..dependencies import get_db, get_current_user
from ..models.rating import Rating
from ..models.menu import MealType
from ..models.vote import Vote
from ..schemas.rating import RatingCreate, RatingResponse

router = APIRouter(prefix="/api/ratings", tags=["Ratings"])

def get_rating_start(meal_type_id: int, meal_date: date, db: Session):
    mt = db.query(MealType).filter(MealType.id == meal_type_id).first()
    if not mt or not mt.end_time or mt.rating_start_hours is None:
        return None
    start = datetime.combine(meal_date, mt.end_time)
    return start + timedelta(hours=mt.rating_start_hours)

def check_rating_open(meal_type_id: int, meal_date: date, db: Session) -> bool:
    start = get_rating_start(meal_type_id, meal_date, db)
    if not start: return False
    return datetime.now() >= start

@router.get("/date/{rating_date}", response_model=list[RatingResponse])
def get_ratings(rating_date: date, db: Session = Depends(get_db)):
    return db.query(Rating).filter(Rating.date == rating_date).all()

@router.get("/my/{rating_date}", response_model=list[RatingResponse])
def get_my_ratings(rating_date: date, db: Session = Depends(get_db),
                   current_user=Depends(get_current_user)):
    return db.query(Rating).filter(
        Rating.date == rating_date,
        Rating.user_id == current_user.id
    ).all()

@router.post("", response_model=RatingResponse)
def create_rating(req: RatingCreate, db: Session = Depends(get_db),
                  current_user=Depends(get_current_user)):
    if not check_rating_open(req.meal_type_id, req.date, db):
        raise HTTPException(status_code=403, detail="Rating not open yet")
    vote = db.query(Vote).filter(
        Vote.user_id == current_user.id,
        Vote.meal_type_id == req.meal_type_id,
        Vote.vote_date == req.date
    ).first()
    if not vote:
        raise HTTPException(status_code=403, detail="You must vote before rating")
    if req.rating < 1 or req.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be 1-5")
    existing = db.query(Rating).filter(
        Rating.user_id == current_user.id,
        Rating.menu_item_id == req.menu_item_id,
        Rating.meal_type_id == req.meal_type_id,
        Rating.date == req.date
    ).first()
    if existing:
        existing.rating = req.rating
        existing.review = req.review
        db.commit(); db.refresh(existing)
        return RatingResponse.model_validate(existing)
    rating = Rating(user_id=current_user.id, **req.model_dump())
    db.add(rating); db.commit(); db.refresh(rating)
    return RatingResponse.model_validate(rating)
