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
from app.timeutils import APP_TIMEZONE
from datetime import date, datetime, time

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Frozen clock (12:00 local) + fixture meal times 13:00-11:00 keep the voting,
# attendance and rating windows all open, so tests don't depend on wall time.
FROZEN_NOW = datetime.combine(date.today(), time(12, 0), tzinfo=APP_TIMEZONE)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def freeze_clock(monkeypatch):
    for module in ("app.api.attendance", "app.api.votes", "app.api.ratings"):
        monkeypatch.setattr(f"{module}.local_now", lambda: FROZEN_NOW)
    yield

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
            MealType(name="Breakfast", start_time=time(13, 0), end_time=time(11, 0), vote_cutoff_hours=0,
                     vote_open_interval_days=14, rating_start_hours=0, attendance_buffer_hours=24, sort_order=1),
            MealType(name="Lunch", start_time=time(13, 0), end_time=time(11, 0), vote_cutoff_hours=0,
                     vote_open_interval_days=14, rating_start_hours=0, attendance_buffer_hours=24, sort_order=2),
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
def voted(client, admin_headers):
    """Create a menu item and have user1/user2 vote for meal 1 today.

    Attendance and ratings require an existing vote for the same user/meal/date.
    """
    today = str(date.today())
    item = client.post("/api/menu-items", headers=admin_headers, json={
        "meal_type_id": 1, "item_name": "Test Food", "date": today
    }).json()
    for username in ("user1", "user2"):
        token = client.post("/api/auth/login", json={
            "username": username, "password": "PasswordToBeChanged"
        }).json()["access_token"]
        client.post("/api/votes", headers={"Authorization": f"Bearer {token}"}, json={
            "menu_item_id": item["id"], "meal_type_id": 1, "vote_date": today
        })
    return item

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
