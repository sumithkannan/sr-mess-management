from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from ..dependencies import get_db, get_current_user, admin_required
from ..models.user import User
from ..schemas.user import UserCreate, UserUpdate, UserResponse

router = APIRouter(prefix="/api/users", tags=["Users"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.get("/active")
def list_active_users(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    users = db.query(User).filter(User.is_active == True).all()
    return [{"id": u.id, "name": u.name, "username": u.username} for u in users]

@router.get("", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db), admin=Depends(admin_required)):
    return db.query(User).all()

@router.post("", response_model=UserResponse)
def create_user(req: UserCreate, db: Session = Depends(get_db), admin=Depends(admin_required)):
    if db.query(User).filter(User.username == req.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    password = req.password if req.password else "PasswordToBeChanged"
    user = User(
        username=req.username, name=req.name, email=req.email, phone=req.phone,
        password_hash=pwd_context.hash(password)
    )
    db.add(user); db.commit(); db.refresh(user)
    return UserResponse.model_validate(user)

@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, req: UserUpdate, db: Session = Depends(get_db), admin=Depends(admin_required)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if req.name is not None: user.name = req.name
    if req.email is not None: user.email = req.email
    if req.phone is not None: user.phone = req.phone
    if req.password: user.password_hash = pwd_context.hash(req.password)
    db.commit(); db.refresh(user)
    return UserResponse.model_validate(user)

@router.patch("/{user_id}/suspend")
def suspend_user(user_id: int, db: Session = Depends(get_db), admin=Depends(admin_required)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user: raise HTTPException(status_code=404)
    user.is_active = False; db.commit()
    return {"message": "User suspended"}

@router.patch("/{user_id}/activate")
def activate_user(user_id: int, db: Session = Depends(get_db), admin=Depends(admin_required)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user: raise HTTPException(status_code=404)
    user.is_active = True; db.commit()
    return {"message": "User activated"}

@router.patch("/{user_id}/role")
def change_role(user_id: int, role: str, db: Session = Depends(get_db), admin=Depends(admin_required)):
    if role not in ["admin", "user"]:
        raise HTTPException(status_code=400, detail="Invalid role")
    user = db.query(User).filter(User.id == user_id).first()
    if not user: raise HTTPException(status_code=404)
    user.role = role; db.commit()
    return {"message": f"Role changed to {role}"}

@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), admin=Depends(admin_required)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user: raise HTTPException(status_code=404)
    db.delete(user); db.commit()
    return {"message": "User deleted"}
