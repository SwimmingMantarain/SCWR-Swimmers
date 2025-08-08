from fastapi import APIRouter, Request, Header, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Annotated, Union
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from api import db
import bcrypt
import secrets
import os


router = APIRouter()
templates = Jinja2Templates(directory="templates")

load_dotenv()
pw = os.getenv("PASSWORD").encode()

TOKEN_LIFETIME = timedelta(hours=1)
active_tokens = {} # token: expiry

def verify_token(token: str | None) -> bool:
    if not token: return False
    expiry = active_tokens.get(token)
    if not expiry:
        return False
    if datetime.now(timezone.utc) > expiry:
        del active_tokens[token]
        return False
    return True

@router.post("/admin", response_class=HTMLResponse)
async def admin_login_post(request: Request, password: str = Form(...)):
    if bcrypt.checkpw(password.encode('utf-8'), pw):
        token = secrets.token_urlsafe(128);
        active_tokens[token] = datetime.now(timezone.utc) + TOKEN_LIFETIME
        response = templates.TemplateResponse(
            request=request, name="admin/dashboard.html"
        )
        response.set_cookie(key="access_token", value=token, httponly=True, max_age=3600)
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
            swimmers = db.get_all_from('scwr_swimmers')
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
            swimmers = db.get_all_from('scwr_swimmers')
            return templates.TemplateResponse(
                request=request, name="admin/view_db.html", context = {"swimmers": swimmers}
            )
        else:
            return RedirectResponse(url="/admin", status_code=302)
