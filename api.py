from fastapi import APIRouter, Request, Header, Security, HTTPException, status, Depends, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security.api_key import APIKeyCookie
from sqlalchemy.orm import Session
from sqlalchemy import select, delete
from typing import Union, Annotated
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from db import ClubSwimmer, ClubSwimmerPb, get_db
from admin import verify_token
from scraper.swimrankings import SwimrankingsScraper
from util import fmt_time, fmt_date
from dotenv import load_dotenv
import os

admin_key_cookie = APIKeyCookie(name="access_token")

load_dotenv()
api_key = os.getenv("APIKEY")
if not api_key:
    raise RuntimeError("APIKEY (secrets.url_safe) not set in .env file!!!\n")

def get_admin_key(db: Session = Depends(get_db), admin_key: str = Security(admin_key_cookie)):
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
        HTTPException: If `admin_key` isn't valid
    """
    if not verify_token(admin_key, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    return admin_key

def verify_api_key(key: str):
    """
    Verifies if an API key exists or is valid

    Args:
        api_key (str): Unique identifier of the API Key

    Returns:
        bool: Whether or not the API key is valid
    """
    return key == api_key


router = APIRouter(prefix="/v1")
templates = Jinja2Templates(directory="templates")

templates.env.filters["fmt_time"] = fmt_time
templates.env.filters["fmt_date"] = fmt_date

@router.post(
    "/add-swimmer",
    response_class=HTMLResponse,
    summary='API endpoint to add a swimmer to db',
    description='Fetches swimmer\'s data from swimranings.net and adds that data to the database.'
)
async def api_add_swimmer(
    request: Request,
    db: Session = Depends(get_db),
    full_name: Annotated[Union[str, None], Header(alias="HX-Prompt")] = None,
    hx_request: Annotated[Union[str, None], Header(alias="HX-Request")] = None
):
    if hx_request:
        swimmer = None
        scraper = SwimrankingsScraper()
        try:
            if not full_name:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No name provided"
                )
            swimmer = await scraper.get_athlete(str(full_name))
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
                gender = swimmer.gender.value
            )
            db.add(swimmer)
            db.commit()

            stmt = select(ClubSwimmer)
            swimmers = db.execute(stmt).scalars().all()

            pbs = await scraper.get_athlete_pbs(swimmer.sw_id)

            for pb in pbs:
                scraped_pb = ClubSwimmerPb(
                    athlete_id = swimmer.id,
                    sw_style_id = pb.sw_style_id,
                    sw_result_id = pb.sw_result_id,
                    sw_meet_id = pb.sw_meet_id,
                    sw_default_fina = pb.sw_default_fina,
                    event = pb.event,
                    course = pb.course,
                    time = pb.time,
                    pts = pb.pts,
                    date = pb.date,
                    city = pb.city,
                    meet_name = pb.meet_name,
                    last_scraped = pb.last_scraped
                )

                stmt = select(ClubSwimmerPb).filter_by(sw_result_id=scraped_pb.sw_result_id)
                existing = db.execute(stmt).scalar_one_or_none()

                if existing is None:
                    db.add(scraped_pb)
                else:
                    fields = ("athlete_id","sw_style_id","sw_meet_id","sw_default_fina","event",
                              "course","time","pts","date","city","meet_name","last_scraped")

                    for f in fields:
                        if getattr(existing, f) != getattr(scraped_pb, f):
                            setattr(existing, f, getattr(scraped_pb, f))

            db.commit()


            return templates.TemplateResponse(
                request=request, name="htmx/admin_view_db.html", context = {"swimmers": swimmers}
            )
        else:
            return RedirectResponse('/admin/view-db', status_code=302)

@router.post(
    "/remove-athlete",
    response_class=HTMLResponse,
    summary='API endpoint to remove a swimmer from db',
    description='Takes in the swimmer\'s first name, finds them in the db and removes them.'
)
async def api_remove_athlete(
    request: Request,
    db: Session = Depends(get_db),
    swimmer_id: int = Form(...),
    hx_request: Annotated[Union[str, None], Header(alias="HX-Request")] = None
):
    if hx_request:
        stmt = select(ClubSwimmer).filter_by(id=swimmer_id)
        swimmer = db.execute(stmt).scalar_one_or_none()

        if swimmer is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Athlete not found")

        db.execute(delete(ClubSwimmerPb).filter_by(athlete_id=swimmer.id))
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
    hx_request: Annotated[Union[str, None], Header()] = None
):
    if hx_request:
        scraper = SwimrankingsScraper()
        try:
            swimmers = await scraper.get_club_athletes()
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

            stmt = delete(ClubSwimmer).where(ClubSwimmer.sw_id.notin_(sw_ids))
            db.execute(stmt)
            db.commit()

            stmt = select(ClubSwimmer)
            swimmers = db.execute(stmt).scalars().all()

            for swimmer in swimmers:
                pbs = await scraper.get_athlete_pbs(swimmer.sw_id)

                for pb in pbs:
                    scraped_pb = ClubSwimmerPb(
                        athlete_id = swimmer.id,
                        sw_style_id = pb.sw_style_id,
                        sw_result_id = pb.sw_result_id,
                        sw_meet_id = pb.sw_meet_id,
                        sw_default_fina = pb.sw_default_fina,
                        event = pb.event,
                        course = pb.course,
                        time = pb.time,
                        pts = pb.pts,
                        date = pb.date,
                        city = pb.city,
                        meet_name = pb.meet_name,
                        last_scraped = pb.last_scraped
                    )

                    stmt = select(ClubSwimmerPb).filter_by(sw_result_id=scraped_pb.sw_result_id)
                    existing = db.execute(stmt).scalar_one_or_none()

                    if existing is None:
                        db.add(scraped_pb)
                    else:
                        fields = ("athlete_id","sw_style_id","sw_meet_id","sw_default_fina","event",
                                  "course","time","pts","date","city","meet_name","last_scraped")

                        for f in fields:
                            if getattr(existing, f) != getattr(scraped_pb, f):
                                setattr(existing, f, getattr(scraped_pb, f))

                db.commit()


            return templates.TemplateResponse(
                request=request, name="htmx/admin_view_db.html", context = {"swimmers": swimmers}
            )
    else:
        return RedirectResponse(
            "/", status_code=status.HTTP_403_FORBIDDEN
        )

@router.post(
    "/get-swimmer-pbs",
    response_class=HTMLResponse,
    summary="Returns an html table with the athlete's pbs",
    description="What more can I say?"
)
async def api_athlete_pb_table(
    request: Request,
    db: Session = Depends(get_db),
    swimmer_id: int = Form(...),
    hx_request: Annotated[Union[str, None], Header()] = None
):
    if hx_request:
        stmt = select(ClubSwimmer).filter_by(id=swimmer_id)
        swimmer = db.execute(stmt).scalar_one_or_none()

        if swimmer:
            stmt = select(ClubSwimmerPb).filter_by(athlete_id=swimmer.id)
            pbs = db.execute(stmt).scalars().all()

            return templates.TemplateResponse(
                request=request, name="htmx/admin_view_pbs.html", context = {"pbs": pbs}
            )
        else:
            return HTMLResponse(
                '<script>window.location.href="https://youtu.be/dQw4w9WgXcQ?si=JPPysw3QXTLBs71z"; window.location.reload()</script>'
            )


@router.get(
    "/athletes",
    response_class=JSONResponse,
    summary="Returns json data of athletes in the database",
    description="TODO: WIP"
)
async def api_athletes_endpoint(
    _: Request,
    db: Session = Depends(get_db),
    x_api_key: str = Header(None),
):
    if x_api_key != api_key:
        return {"message" : "¯\\_(ツ)_/¯"}

    stmt = select(ClubSwimmer)
    swimmers = db.execute(stmt).scalars().all()

    return swimmers

@router.get(
    "/athlete",
    response_class=JSONResponse,
    summary="Returns json data for specific athlete",
    description="TODO: WIP"
)
async def api_athlete_endpoint(
        _: Request,
        id: int,
        db: Session = Depends(get_db),
        x_api_key: str = Header(None),
):
    if x_api_key != api_key:
        return {"message" : "¯\\_(ツ)_/¯"}

    stmt = select(ClubSwimmer).filter_by(id=id)
    athlete = db.execute(stmt).scalar_one_or_none()

    stmt = select(ClubSwimmerPb).filter_by(athlete_id=athlete.id)
    athlete_pbs = db.execute(stmt).scalars().all()

    return {"athlete": athlete, "pbs": athlete_pbs}
