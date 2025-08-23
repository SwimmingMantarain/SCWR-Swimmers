from fastapi import APIRouter, Request, Header, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Annotated, Union
from sqlalchemy import select
from sqlalchemy.orm import Session
from db import get_db, ClubSwimmer

router = APIRouter(prefix="/htmx")
templates = Jinja2Templates(directory='templates/htmx')

@router.get(
    "/page/home",
    response_class=HTMLResponse,
    summary='Returns the home page htmx fragment',
    description='What more can I say?'
)
async def htmx_home(request: Request, hx_request: Annotated[Union[str, None], Header()] = None):
    if hx_request:
        response = templates.TemplateResponse(
            request=request, name="index.html"
        )

        response.headers["Hx-Push-Url"] = "/"

        return response

@router.get(
    "/page/athletes",
    response_class=HTMLResponse,
    summary='Returns the athletes page htmx fragment',
    description='The page is just a list of swimmers in the db.'
)
async def htmx_athletes_page(
    request: Request,
    db: Session = Depends(get_db),
    hx_request: Annotated[Union[str, None], Header()] = None
):
    stmt = select(ClubSwimmer)
    swimmers = db.execute(stmt).scalars().all()

    if hx_request:
        response = templates.TemplateResponse(
            request=request, name="athletes.html", context={'swimmers': swimmers}
        )

        response.headers["HX-Push-Url"] = "/athletes"

        return response

@router.get(
    "/page/athlete",
    response_class=HTMLResponse,
    summary='Returns portfolio of a specific swimmer as an htmx fragment',
    description='Uses the `swimmer_id` to fetch data about that swimmer from the db. If that id isn\'t in the db, user gets redirected back to `/athletes`.'
)
async def htmx_specific_athlete_page(
    request: Request,
    sw_id: int,
    db: Session = Depends(get_db),
    hx_request: Annotated[Union[str, None], Header()] = None
):
    stmt = select(ClubSwimmer).filter_by(sw_id=sw_id)
    swimmer = db.execute(stmt).scalar_one_or_none()
    if swimmer:
        if hx_request:
            response = templates.TemplateResponse(
                request=request, name="athlete.html", context={'swimmer': swimmer}
            )

            response.headers["HX-Push-Url"] = f"/athlete?sw_id={sw_id}"

            return response
    else:
        return RedirectResponse("/athletes", status_code=302)

@router.get(
    "/page/records",
    response_class=HTMLResponse,
    summary='Returns the club records page htmx fragment',
    description='W.I.P.'
)
async def htmx_records_page(request: Request, hx_request: Annotated[Union[str, None], Header()] = None):
    if hx_request:
        response = templates.TemplateResponse(
            request=request, name="records.html"
        )

        response.headers["Hx-Push-Url"] = "/records"

        return response

@router.get(
    "/page/meets",
    response_class=HTMLResponse,
    summary='Returns the meets page htmx fragment',
    description='W.I.P.'
)
async def meets_page(request: Request, hx_request: Annotated[Union[str, None], Header()] = None):
    if hx_request:
        response = templates.TemplateResponse(
            request=request, name="meets.html"
        )

        response.headers["HX-Push-Url"] = "/meets"

        return response
