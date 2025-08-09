from fastapi import APIRouter, Request, Header
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Annotated, Union
from api import db
import random

from db import ClubSwimmer

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
    swimmers = db.query(ClubSwimmer).all()
    if swimmers:
        random.shuffle(swimmers)

    if hx_request:
        return templates.TemplateResponse(
            request=request, name="htmx/athletes.html", context={'swimmers': swimmers}
        )
    return templates.TemplateResponse(
        request=request, name="athletes.html", context={'swimmers': swimmers}
    )

@router.get("/athletes/{swimmer_id}", response_class=HTMLResponse)
async def specific_athlete_page(request: Request, hx_request: Annotated[Union[str, None], Header()] = None, swimmer_id: int = 0):
    swimmer = db.query(ClubSwimmer).filter_by(id=swimmer_id)
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
