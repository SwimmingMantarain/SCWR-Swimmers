import sqlite3
from fastapi import APIRouter, File, Request, Header, UploadFile, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Union, Annotated
import swimrankings

router = APIRouter(prefix="/v1")

templates = Jinja2Templates(directory="templates")

db = sqlite3.connect("scwr.sql")
cursor = db.cursor()

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

# Enable foreign keys
query = """
PRAGMA foreign_keys = ON;
"""
cursor.execute(query);

query = """
CREATE TABLE IF NOT EXISTS swimmer_photos (
    id INTEGER PRIMARY KEY,
    data BLOB NOT NULL,
    swimmer_sql_id INTEGER NOT NULL,
    FOREIGN KEY(swimmer_sql_id) REFERENCES swimmers(id)
)
"""
cursor.execute(query)

@router.post("/add-swimmer-photo")
async def api_add_swimmer_photo(full_name: str = Form(...), photo: UploadFile = File(...)):
    query = "SELECT id FROM swimmers WHERE first_name = ? AND last_name = ?;"
    first_name, last_name = full_name.split(',')
    cursor.execute(query, (first_name, last_name))
    swimmer_id = int(cursor.fetchall()[0][0])
    photo_bytes = await photo.read()

    query = """INSERT INTO swimmer_photos(data, swimmer_sql_id)
               VALUES(?, ?);"""
    cursor.execute(query, (photo_bytes, swimmer_id))
    db.commit()


@router.post("/add-swimmer", response_class=HTMLResponse)
async def api_add_swimmer(request: Request, full_name: Annotated[Union[str, None], Header(alias="HX-Prompt")] = None, hx_request: Annotated[Union[str, None], Header(alias="HX-Request")] = None):
    if hx_request:
        swimmer = swimrankings.get_swimmer(full_name)

        if swimmer:
            query = """INSERT INTO swimmers(sw_id, birth_year, first_name, last_name)
                       VALUES(?, ?, ?, ?);"""
            cursor.execute(query, (swimmer[0], swimmer[1], swimmer[2], swimmer[3]))

            db.commit()

            query = "SELECT * FROM swimmers"
            cursor.execute(query)
            swimmers = cursor.fetchall()
            return templates.TemplateResponse(
                request=request, name="htmx/admin_view_db.html", context = {"swimmers": swimmers}
            )

@router.post("/remove-swimmer", response_class=HTMLResponse)
async def api_remove_swimmer(request: Request, first_name: Annotated[Union[str, None], Header(alias="HX-Prompt")] = None, hx_request: Annotated[Union[str, None], Header(alias="HX-Request")] = None):
    if hx_request:
        query = "DELETE FROM swimmers WHERE first_name = ?;"
        cursor.execute(query, (first_name,))

        db.commit()

        query = "SELECT * FROM swimmers"
        cursor.execute(query)
        swimmers = cursor.fetchall()
        return templates.TemplateResponse(
            request=request, name="htmx/admin_view_db.html", context = {"swimmers": swimmers}
        )


@router.post("/sync-swimmers", response_class=HTMLResponse)
async def api_sync_swimmers(request: Request, hx_request: Annotated[Union[str, None], Header()] = None):
    swimmers = swimrankings.get_scwr_swimmers()
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
