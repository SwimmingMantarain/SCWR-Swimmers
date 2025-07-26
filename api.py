import sqlite3
from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import bcrypt

router = APIRouter()

templates = Jinja2Templates(directory="templates")

# Creates one if it doesn't exist
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

pw = b'$2b$12$9BhNNcsswdTbqEOI6qUI3.6DOwzFS.ZIRcEn9nSIFlXKRK5qPVxwO'

@router.post("/admin", response_class=HTMLResponse)
async def admin_login(request: Request, password: str = Form(...)):
    if bcrypt.checkpw(password.encode('utf-8'), pw):
        token = 'secure'
        response = templates.TemplateResponse(
            request=request, name="admin/dashboard.html"
        )
        response.set_cookie(key="access_token", value=token, httponly=True, max_age=3600)
        return response
    return templates.TemplateResponse(
        request=request, name="htmx/admin_login.html"
    )
