from passlib.context import CryptContext
from ..database import SessionLocal
from ..models.user import User


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def seed_admin():
    db = SessionLocal()
    try:
        if db.query(User).count() == 0:
            admin = User(
                username="admin",
                name="Admin",
                email="admin@mess.com",
                password_hash=pwd_context.hash("PasswordToBeChanged"),
                role="admin",
                is_active=True
            )
            db.add(admin)
            db.commit()
            print("Default admin created (admin / PasswordToBeChanged)")
    finally:
        db.close()
