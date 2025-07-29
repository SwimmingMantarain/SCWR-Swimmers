import sqlite3
from fastapi import APIRouter, File, Request, Header, UploadFile, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Union, Annotated
import swimrankings
import base64
import imghdr

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

@router.post("/remove-swimmer-photo", response_class=HTMLResponse)
async def api_remove_swimmer_photo(request: Request, photo_id: int = Form(...), hx_request: Annotated[Union[str, None], Header()] = None):
    if hx_request:
        query = "SELECT swimmer_sql_id FROM swimmer_photos WHERE id = ?;"
        cursor.execute(query, (photo_id,))
        swimmer_id = int(cursor.fetchall()[0][0])
        query = "DELETE FROM swimmer_photos WHERE id = ?;"
        cursor.execute(query, (photo_id,))

        db.commit()

        query = "SELECT * FROM swimmer_photos WHERE swimmer_sql_id = ?;"
        cursor.execute(query, (swimmer_id,))
        photos = cursor.fetchall()

        if photos:
            base64_photos = []
            for photo in photos:
                base64_photos.append(
                    (photo[0], base64.b64encode(photo[1]).decode('utf-8'), imghdr.what(None, h=photo[1]),photo[2])
                )
                print(type(photo[1]))
            return templates.TemplateResponse(
                request=request, name="htmx/admin_view_swimmer_photos.html", context={"photos": base64_photos}
            )




@router.post("/get-swimmer-photos", response_class=HTMLResponse)
async def api_get_swimmer_photos(request: Request, full_name: str = Form(...), hx_request: Annotated[Union[str, None], Header()] = None):
    if hx_request:
        first_name, last_name = full_name.split(',')
        query = "SELECT id FROM swimmers WHERE first_name = ? AND last_name = ?;"
        cursor.execute(query, (first_name, last_name))
        swimmer_id = int(cursor.fetchall()[0][0])

        query = "SELECT * FROM swimmer_photos WHERE swimmer_sql_id = ?;"
        cursor.execute(query, (swimmer_id,))
        photos = cursor.fetchall()

        if photos:
            base64_photos = []
            for photo in photos:
                base64_photos.append(
                    (photo[0], base64.b64encode(photo[1]).decode('utf-8'), imghdr.what(None, h=photo[1]),photo[2])
                )
                print(type(photo[1]))
            return templates.TemplateResponse(
                request=request, name="htmx/admin_view_swimmer_photos.html", context={"photos": base64_photos}
            )


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
