from fastapi import APIRouter, Request, Header, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Annotated, Union
from datetime import datetime, timedelta, timezone
from typing import Optional
from db import Token, db, ClubSwimmer
from dotenv import load_dotenv
import bcrypt
import secrets
import os



router = APIRouter()
templates = Jinja2Templates(directory="templates")

load_dotenv()
pw_hash = os.getenv("PASSWORD")
if not pw_hash:
    raise RuntimeError("PASSWORD (bcrypt hash) is not set in .env!!!\n")
pw = pw_hash.encode()

TOKEN_LIFETIME = timedelta(hours=1)
COOKIE_MAX_AGE = int(TOKEN_LIFETIME.total_seconds())

def verify_token(token_str: Optional[str]) -> bool:
    if not token_str:
        return False

    token = db.query(Token).filter_by(token=token_str).first()

    if not token:
        return False

    expiry = token.expiry

    # TODO: Fix for Postgres Migration
    if expiry.tzinfo is None:
        expiry = expiry.replace(tzinfo=timezone.utc)

    if datetime.now(timezone.utc) > expiry:
        db.rm(token)
        db.session.commit()
        return False

    return True

@router.post("/admin", response_class=HTMLResponse)
async def admin_login_post(request: Request, password: str = Form(...)):
    if bcrypt.checkpw(password.encode('utf-8'), pw):
        token_str = secrets.token_urlsafe(32)
        expiry = datetime.now(timezone.utc) + TOKEN_LIFETIME

        token = Token(
            token = token_str,
            expiry = expiry
        )

        db.add(token)
        db.session.commit()

        response = templates.TemplateResponse(
            request=request, name="admin/dashboard.html"
        )

        response.set_cookie(
            key="access_token",
            value=token_str,
            httponly=True,
            secure=True, # Only https
            samesite="lax", # mitigate csrf
            max_age=COOKIE_MAX_AGE)
        return response
    return templates.TemplateResponse(
        request=request, name="htmx/admin_login.html"
    )


@router.get("/admin", response_class=HTMLResponse)
async def admin_login(request: Request):
    token = request.cookies.get("access_token")

    if verify_token(token):
        return templates.TemplateResponse(
            request=request, name="htmx/dashboard.html"
        )
    return templates.TemplateResponse(
        request=request, name="admin/login.html"
    )

@router.get("/admin/view-db", response_class=HTMLResponse)
async def admin_view_db(request: Request, hx_request: Annotated[Union[str, None], Header()] = None):
    token = request.cookies.get("access_token")

    if hx_request:
        if verify_token(token):
            swimmers = db.query(ClubSwimmer).all()
            return templates.TemplateResponse(
                request=request, name="htmx/admin_view_db.html", context = {"swimmers": swimmers}
            )
        else:
            response = templates.TemplateResponse(
                request=request, name="htmx/admin_login.html"
            )
            response.headers["HX-Push-Url"] = "/admin"
            return response
    else:
        if verify_token(token):
            swimmers = db.query(ClubSwimmer).all()
            return templates.TemplateResponse(
                request=request, name="admin/view_db.html", context = {"swimmers": swimmers}
            )
        else:
            return RedirectResponse(url="/admin", status_code=302)
