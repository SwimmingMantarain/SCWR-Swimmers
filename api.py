from fastapi import APIRouter, File, Request, Header, UploadFile, Form, Security, HTTPException, status, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security.api_key import APIKeyCookie
from sqlalchemy.orm import Session
from typing import Union, Annotated
from db import ClubSwimmer, get_db
from admin import verify_token
import swimrankings

api_key_cookie = APIKeyCookie(name="access_token")

def get_api_key(api_key: str = Security(api_key_cookie)):
    if not verify_token(api_key):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    return api_key

router = APIRouter(prefix="/v1", dependencies=[Depends(get_api_key)])
templates = Jinja2Templates(directory="templates")

@router.post("/add-swimmer", response_class=HTMLResponse)
async def api_add_swimmer(
    request: Request,
    db: Session = Depends(get_db),
    full_name: Annotated[Union[str, None], Header(alias="HX-Prompt")] = None,
    hx_request: Annotated[Union[str, None], Header(alias="HX-Request")] = None
):
    if hx_request:
        swimmer = swimrankings.get_swimmer(full_name)

        if swimmer:
            swimmer = ClubSwimmer(
                sw_id = int(swimmer[0]),
                birth_year = int(swimmer[1]),
                first_name = swimmer[2],
                last_name = swimmer[3],
                gender = int(swimmer[4])
            )
            db.add(swimmer)
            db.commit()

            swimmers = db.query(ClubSwimmer).all()
            return templates.TemplateResponse(
                request=request, name="htmx/admin_view_db.html", context = {"swimmers": swimmers}
            )
        else:
            return RedirectResponse('/admin/view-db', status_code=302)

@router.post("/remove-swimmer", response_class=HTMLResponse)
async def api_remove_swimmer(request: Request, first_name: Annotated[Union[str, None], Header(alias="HX-Prompt")] = None, hx_request: Annotated[Union[str, None], Header(alias="HX-Request")] = None):
    if hx_request:
        swimmer = db.query(ClubSwimmer).filter_by(first_name=first_name).first()
        db.rm(swimmer)
        db.session.commit()

        swimmers = db.query(ClubSwimmer).all()
        return templates.TemplateResponse(
            request=request, name="htmx/admin_view_db.html", context = {"swimmers": swimmers}
        )


@router.post("/sync-swimmers", response_class=HTMLResponse)
async def api_sync_swimmers(request: Request, hx_request: Annotated[Union[str, None], Header()] = None):
    swimmers = swimrankings.get_scwr_swimmers()
    if swimmers:
        for swimmer in swimmers:
            db_swimmer = db.query(ClubSwimmer).filter_by(sw_id=swimmer[0]).first()
            if not db_swimmer:
                swimmer = ClubSwimmer(
                    sw_id = int(swimmer[0]),
                    birth_year = int(swimmer[1]),
                    first_name = swimmer[2],
                    last_name = swimmer[3],
                    gender = int(swimmer[4])
                )

                db.add(swimmer)
                db.session.commit()
        
        # wish there was a cleaner way of doing this
        sw_ids = []
        for swimmer in swimmers:
            sw_ids.append(swimmer[0])

        db.query(ClubSwimmer).filter(ClubSwimmer.sw_id.not_in(sw_ids)).delete(synchronize_session=False)
        db.session.commit()


    if hx_request:
        swimmers = db.query(ClubSwimmer).all()
        return templates.TemplateResponse(
            request=request, name="htmx/admin_view_db.html", context = {"swimmers": swimmers}
        )
