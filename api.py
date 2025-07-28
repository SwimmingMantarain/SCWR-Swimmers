import sqlite3
from fastapi import APIRouter, Form, Request, Header
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Union, Annotated
from swimrankings import get_scwr_swimmers

router = APIRouter(prefix="/v1")

templates = Jinja2Templates(directory="templates")

# Creates one if it doesn't exist
db = sqlite3.connect("scwr.sql")
cursor = db.cursor()

# Create table if it doesn't exist
query = """
CREATE TABLE IF NOT EXISTS swimmers (
    id INTEGER PRIMARY KEY,
    sw_id INTEGER NOT NULL,
    birth_year INTEGER NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL
);
"""
cursor.execute(query) 

@router.post("/add-swimmer", response_class=HTMLResponse)
async def api_add_swimmer(request: Request, full_name: str = Form(...), hx_request: Annotated[Union[str, None], Header()] = None):
    if hx_request:
        print(full_name)

@router.post("/sync-swimmers", response_class=HTMLResponse)
async def api_sync_swimmers(request: Request, hx_request: Annotated[Union[str, None], Header()] = None):
    swimmers = get_scwr_swimmers()
    sw_ids = [swimmer[0] for swimmer in swimmers]
    for swimmer in swimmers:
        query = "SELECT * FROM swimmers WHERE sw_id = ?"
        cursor.execute(query, (swimmer[0],))
        db_swimmer = cursor.fetchall()
        if not db_swimmer:
            query = """INSERT INTO swimmers(sw_id, birth_year, first_name, last_name)
                        VALUES(?, ?, ?, ?);"""
            cursor.execute(query, (swimmer[0], swimmer[1], swimmer[2], swimmer[3]))

    # disgusting
    placeholders = ', '.join(['?'] * len(sw_ids))
    query = f"DELETE FROM swimmers WHERE sw_id NOT IN ({placeholders});"
    cursor.execute(query, sw_ids)

    db.commit()

    if hx_request:
        query = "SELECT * FROM swimmers"
        cursor.execute(query)
        swimmers = cursor.fetchall()
        return templates.TemplateResponse(
            request=request, name="htmx/admin_view_db.html", context = {"swimmers": swimmers}
        )
