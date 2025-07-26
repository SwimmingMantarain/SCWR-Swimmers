import sqlite3
from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Creates one if it doesn't exist
# (DB logic can be removed if not needed for login)
db = sqlite3.connect("swimmers.sql")
cursor = db.cursor()

# Create table if it doesn't exist
query = """
CREATE TABLE IF NOT EXISTS swimmers (
    id INTEGER PRIMARY KEY,
    todo_text TEXT NOT NULL,
    done BOOL DEFAULT FALSE
);
"""
cursor.execute(query)

pwd = '$2b$12$ciLpR10DrFiKDjRlgbkrDu3QYNRzkOE/lOMUtkd4OSRpzyHbF3iHa'
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/admin", response_class=HTMLResponse)
async def admin_login(request: Request, password: str = Form(...)):
    error = None
    if not pwd_context.verify(password, pwd):
        error = "Wrong password. Try again, maybe it's BANANA?"
        return templates.TemplateResponse(
            "admin_login.html", {"request": request, "error": error}, status_code=401
        )
    # On success, redirect to admin dashboard (or admin page)
    response = RedirectResponse(url="/admin/dashboard", status_code=303)
    return response 