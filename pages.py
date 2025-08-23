from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import select
from db import get_db, ClubSwimmer

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get(
    "/",
    response_class=HTMLResponse,
    summary='Returns the home page',
    description='What more can I say?'
)
async def index(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html"
    )

@router.get(
    "/athletes",
    response_class=HTMLResponse,
    summary='Returns the athletes page',
    description='The page is just a list of swimmers in the db.'
)
async def athletes_page(
    request: Request,
    db: Session = Depends(get_db),
):
    stmt = select(ClubSwimmer)
    swimmers = db.execute(stmt).scalars().all()

    return templates.TemplateResponse(
        request=request, name="athletes.html", context={'swimmers': swimmers}
    )

@router.get(
    "/athlete",
    response_class=HTMLResponse,
    summary='Returns portfolio of a specific swimmer',
    description='Uses the `sw_id` to fetch data about that swimmer from the db. If that id isn\'t in the db, user gets redirected back to `/athletes`.'
)
async def specific_athlete_page(
    request: Request,
    sw_id: int,
    db: Session = Depends(get_db),
):
    stmt = select(ClubSwimmer).filter_by(sw_id=sw_id)
    swimmer = db.execute(stmt).scalar_one_or_none()
    if swimmer:
        return templates.TemplateResponse(
            request=request, name="athlete.html", context={'swimmer': swimmer}
        )
    
    else:
        return RedirectResponse("/athletes", status_code=302)

@router.get(
    "/records",
    response_class=HTMLResponse,
    summary='Returns the club records page',
    description='W.I.P.'
)
async def records_page(request: Request):
    return templates.TemplateResponse(
        request=request, name="records.html"
    )

@router.get(
    "/meets",
    response_class=HTMLResponse,
    summary='Returns the meets page',
    description='W.I.P.'
)
async def meets_page(request: Request):
    return templates.TemplateResponse(
        request=request, name="meets.html"
    )
