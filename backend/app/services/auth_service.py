from passlib.context import CryptContext
from ..database import SessionLocal
from ..models.user import User


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def seed_admin():
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == "admin").first()
        if admin is None:
            admin = User(
                username="admin",
                name="Admin",
                email="admin@mess.com",
                password_hash=pwd_context.hash("PasswordToBeChanged"),
                role="admin",
                is_active=True
            )
            db.add(admin)
            print("Default admin created (admin / PasswordToBeChanged)")
        else:
            admin.name = admin.name or "Admin"
            admin.email = admin.email or "admin@mess.com"
            admin.role = "admin"
            admin.is_active = True
            if not admin.password_hash or not pwd_context.verify("PasswordToBeChanged", admin.password_hash):
                admin.password_hash = pwd_context.hash("PasswordToBeChanged")
            print("Default admin ensured active (admin / PasswordToBeChanged)")
        db.commit()
    finally:
        db.close()
