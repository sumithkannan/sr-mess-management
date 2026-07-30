import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import inspect, text
from .database import engine, Base
from .api import auth, users, menu, votes, attendance, ratings, mess_duty, expenses, reports, configurations, off_days
from .services.auth_service import seed_admin
from .config import settings

logging.basicConfig(level=logging.ERROR, format="%(asctime)s [%(levelname)s] %(message)s")

def _add_col_if_missing(conn, table, col, col_def):
    try:
        conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col_def}"))
        conn.commit()
        logging.info(f"Added column {col} to {table}")
    except Exception:
        pass

def migrate_schema():
    inspector = inspect(engine)
    if "meal_types" not in inspector.get_table_names():
        return
    cols = {c["name"] for c in inspector.get_columns("meal_types")}
    with engine.connect() as conn:
        if "start_time" not in cols:
            _add_col_if_missing(conn, "meal_types", "start_time", "start_time TIME")
            _add_col_if_missing(conn, "meal_types", "end_time", "end_time TIME")
            _add_col_if_missing(conn, "meal_types", "vote_cutoff_hours", "vote_cutoff_hours INTEGER DEFAULT 12")
            _add_col_if_missing(conn, "meal_types", "rating_start_hours", "rating_start_hours INTEGER DEFAULT 2")
        if "vote_open_interval_days" not in cols:
            _add_col_if_missing(conn, "meal_types", "vote_open_interval_days", "vote_open_interval_days INTEGER DEFAULT 7")

Base.metadata.create_all(bind=engine)
migrate_schema()
seed_admin()

app = FastAPI(title="Mess Management System", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(menu.router)
app.include_router(votes.router)
app.include_router(attendance.router)
app.include_router(ratings.router)
app.include_router(mess_duty.router)
app.include_router(expenses.router)
app.include_router(reports.router)
app.include_router(configurations.router)
app.include_router(off_days.router)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logging.error("Unhandled exception on %s %s", request.method, request.url, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )

@app.get("/api/health")
def health():
    return {"status": "ok", "app": "Mess Management System"}
