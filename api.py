from fastapi import APIRouter, Request, Header, Security, HTTPException, status, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security.api_key import APIKeyCookie
from sqlalchemy.orm import Session
from sqlalchemy import select, delete
from swimrankings import SwimrankingsScraper, get_scraper
from typing import Union, Annotated
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from db import ClubSwimmer, get_db
from admin import verify_token

api_key_cookie = APIKeyCookie(name="access_token")

def get_api_key(db: Session = Depends(get_db), api_key: str = Security(api_key_cookie)):
    """
    Checks whether user has valid credentials

    Side effects:
    - Calls `verify_token` which deletes expired tokens and commits the change

    Args:
        db (Session): SQLAlchemy database session.
        api_key (str): The api token to verify

    Returns:
        str: The api key

    Raises:
        HTTPException: If `api_key` isn't valid
    """
    if not verify_token(api_key, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    return api_key

router = APIRouter(prefix="/v1", dependencies=[Depends(get_api_key)])
templates = Jinja2Templates(directory="templates")

@router.post(
    "/add-swimmer",
    response_class=HTMLResponse,
    summary='API endpoint to add a swimmer to db',
    description='Fetches swimmer\'s data from swimranings.net and adds that data to the database.'
)
async def api_add_swimmer(
    request: Request,
    db: Session = Depends(get_db),
    scraper: SwimrankingsScraper = Depends(get_scraper),
    full_name: Annotated[Union[str, None], Header(alias="HX-Prompt")] = None,
    hx_request: Annotated[Union[str, None], Header(alias="HX-Request")] = None
):
    if hx_request:
        swimmer = None
        try:
            if full_name:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No name provided"
                )
            swimmer = await scraper.get_swimmer(str(full_name))
        except RuntimeError as e:
            print(e)
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to scrape swimrankings.net"
            )

        if swimmer:
            swimmer = ClubSwimmer(
                sw_id = swimmer.sw_id,
                birth_year = swimmer.birth_year,
                first_name = swimmer.first_name,
                last_name = swimmer.last_name,
                gender = swimmer.gender
            )
            db.add(swimmer)
            db.commit()

            stmt = select(ClubSwimmer)
            swimmers = db.execute(stmt).scalars().all()
            return templates.TemplateResponse(
                request=request, name="htmx/admin_view_db.html", context = {"swimmers": swimmers}
            )
        else:
            return RedirectResponse('/admin/view-db', status_code=302)

@router.post(
    "/remove-swimmer",
    response_class=HTMLResponse,
    summary='API endpoint to remove a swimmer from db',
    description='Takes in the swimmer\'s first name, finds them in the db and removes them.'
)
async def api_remove_swimmer(
    request: Request,
    db: Session = Depends(get_db),
    first_name: Annotated[Union[str, None], Header(alias="HX-Prompt")] = None,
    hx_request: Annotated[Union[str, None], Header(alias="HX-Request")] = None
):
    if hx_request:
        stmt = select(ClubSwimmer).filter_by(first_name=first_name)
        swimmer = db.execute(stmt).scalar_one_or_none()
        db.delete(swimmer)
        db.commit()

        swimmers = db.query(ClubSwimmer).all()
        return templates.TemplateResponse(
            request=request, name="htmx/admin_view_db.html", context = {"swimmers": swimmers}
        )


@router.post(
    "/sync-swimmers",
    response_class=HTMLResponse,
    summary='API endpoint to sync current swimmers in db with ones registered in swimrankings.net',
    description='Updates the database entries of the swimmers based on what gets scraped from swimrankings.net. If a new swimmer appears, they get added to the db. If one disappears, they are removed from the db.'
)
async def api_sync_swimmers(
    request: Request,
    db: Session = Depends(get_db),
    scraper: SwimrankingsScraper = Depends(get_scraper),
    hx_request: Annotated[Union[str, None], Header()] = None
):
    try:
        swimmers = await scraper.get_scwr_swimmers()
    except RuntimeError as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to scrape swimrankings"
        )
    if swimmers:
        for swimmer in swimmers:
            stmt = select(ClubSwimmer).filter_by(sw_id=swimmer.sw_id)
            db_swimmer = db.execute(stmt).scalar_one_or_none()
            if not db_swimmer:
                swimmer = ClubSwimmer(
                    sw_id = swimmer.sw_id,
                    birth_year = swimmer.birth_year,
                    first_name = swimmer.first_name,
                    last_name = swimmer.last_name,
                    gender = swimmer.gender.value
                )

                db.add(swimmer)
                db.commit()
        
        # wish there was a cleaner way of doing this
        sw_ids = []
        for swimmer in swimmers:
            sw_ids.append(swimmer.sw_id)

        stmt = select(ClubSwimmer).filter(ClubSwimmer.sw_id.not_in(sw_ids))
        swimmers = db.execute(stmt).scalars().all()

        stmt = delete(ClubSwimmer).where(ClubSwimmer.sw_id.not_in(sw_ids))
        db.execute(stmt)
        db.commit()


    if hx_request:
        stmt = select(ClubSwimmer)
        swimmers = db.execute(stmt).scalars().all()
        return templates.TemplateResponse(
            request=request, name="htmx/admin_view_db.html", context = {"swimmers": swimmers}
        )
