from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from .database import SessionLocal
from .config import settings
from .models.user import User

security = HTTPBearer()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = int(payload.get("sub"))
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    return user

def admin_required(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

def mess_duty_or_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role == "admin":
        return current_user
    from .models.mess_duty import MessDutyAssignment
    from datetime import date
    db = SessionLocal()
    has_duty = db.query(MessDutyAssignment).filter(
        MessDutyAssignment.user_id == current_user.id,
        MessDutyAssignment.start_date <= date.today(),
        MessDutyAssignment.end_date >= date.today()
    ).first()
    db.close()
    if not has_duty:
        raise HTTPException(status_code=403, detail="Mess duty or admin access required")
    return current_user
