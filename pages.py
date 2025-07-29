from fastapi import APIRouter, Request, Header
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Annotated, Union
from api import cursor
import random
import base64
import imghdr

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def index(request: Request, hx_request: Annotated[Union[str, None], Header()] = None):
    if hx_request:
        return templates.TemplateResponse(
            request=request, name="htmx/index.html"
        )
    return templates.TemplateResponse(
        request=request, name="index.html"
    )

@router.get("/athletes", response_class=HTMLResponse)
async def athletes_page(request: Request, hx_request: Annotated[Union[str, None], Header()] = None):
    query = "SELECT * FROM swimmers;"
    cursor.execute(query)
    swimmers = cursor.fetchall()
    random.shuffle(swimmers)

    swimmers_and_photos = []

    query = "SELECT data FROM swimmer_photos WHERE swimmer_sql_id = ?;"
    for swimmer in swimmers:
        cursor.execute(query, (swimmer[0],))
        data = cursor.fetchone()
        if data:
            swimmers_and_photos.append((swimmer[3], swimmer[4], base64.b64encode(data[0]).decode('utf-8'), imghdr.what(None, h=data[0]), swimmer[0]))
        else:
            swimmers_and_photos.append((swimmer[3], swimmer[4], None, None, swimmer[0]))

    if hx_request:
        return templates.TemplateResponse(
            request=request, name="htmx/athletes.html", context={'sap': swimmers_and_photos}
        )
    return templates.TemplateResponse(
        request=request, name="athletes.html", context={'sap': swimmers_and_photos}
    )

@router.get("/athletes/{swimmer_id}", response_class=HTMLResponse)
async def specific_athlete_page(request: Request, hx_request: Annotated[Union[str, None], Header()] = None, swimmer_id: int = 0):
    query = "SELECT * FROM swimmers WHERE id = ?;"
    cursor.execute(query, (swimmer_id,))
    swimmer = cursor.fetchone()
    if swimmer:
        if hx_request:
            return templates.TemplateResponse(
                request=request, name="htmx/athlete.html", context={'swimmer': swimmer}
            )
        
        return templates.TemplateResponse(
            request=request, name="athlete.html", context={'swimmer': swimmer}
        )
    
    else:
        return RedirectResponse("/athletes", status_code=302)

@router.get("/records", response_class=HTMLResponse)
async def records_page(request: Request, hx_request: Annotated[Union[str, None], Header()] = None):
    if hx_request:
        return templates.TemplateResponse(
            request=request, name="htmx/records.html"
        )
    return templates.TemplateResponse(
        request=request, name="records.html"
    )

@router.get("/meets", response_class=HTMLResponse)
async def meets_page(request: Request, hx_request: Annotated[Union[str, None], Header()] = None):
    if hx_request:
        return templates.TemplateResponse(
            request=request, name="htmx/meets.html"
        )
    return templates.TemplateResponse(
        request=request, name="meets.html"
    )
