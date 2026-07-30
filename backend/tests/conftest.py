import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.main import app
from app.dependencies import get_db
from app.services.auth_service import pwd_context
from app.models.user import User
from app.models.menu import MealType
from datetime import time

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    if db.query(User).count() == 0:
        admin = User(
            username="admin", name="Admin", email="admin@mess.com",
            password_hash=pwd_context.hash("PasswordToBeChanged"),
            role="admin", is_active=True
        )
        db.add(admin)
        user1 = User(
            username="user1", name="User One", email="user1@mess.com",
            password_hash=pwd_context.hash("PasswordToBeChanged"),
            role="user", is_active=True
        )
        db.add(user1)
        user2 = User(
            username="user2", name="User Two", email="user2@mess.com",
            password_hash=pwd_context.hash("PasswordToBeChanged"),
            role="user", is_active=True
        )
        db.add(user2)
        defaults = [
            MealType(name="Breakfast", start_time=time(23, 59), end_time=time(0, 1), vote_cutoff_hours=0, vote_open_interval_days=14, rating_start_hours=0, sort_order=1),
            MealType(name="Lunch", start_time=time(23, 59), end_time=time(23, 59), vote_cutoff_hours=0, vote_open_interval_days=14, rating_start_hours=0, sort_order=2),
        ]
        for mt in defaults:
            db.add(mt)
        db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def admin_token(client):
    r = client.post("/api/auth/login", json={"username": "admin", "password": "PasswordToBeChanged"})
    return r.json()["access_token"]

@pytest.fixture
def user_token(client):
    r = client.post("/api/auth/login", json={"username": "user1", "password": "PasswordToBeChanged"})
    return r.json()["access_token"]

@pytest.fixture
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}

@pytest.fixture
def user_headers(user_token):
    return {"Authorization": f"Bearer {user_token}"}
