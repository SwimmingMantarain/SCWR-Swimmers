import sqlite3
from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse

router = APIRouter()

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

@router.post("/admin", response_class=HTMLResponse)
async def admin_login(request: Request, password: str = Form(...)):
    print(password)
