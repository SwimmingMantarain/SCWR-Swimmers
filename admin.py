from fastapi import APIRouter, Request, Header, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Annotated, Union
from api import db
import bcrypt

router = APIRouter()

templates = Jinja2Templates(directory="templates")

pw = b'$2b$12$9BhNNcsswdTbqEOI6qUI3.6DOwzFS.ZIRcEn9nSIFlXKRK5qPVxwO'

@router.post("/admin", response_class=HTMLResponse)
async def admin_login_post(request: Request, password: str = Form(...)):
    if bcrypt.checkpw(password.encode('utf-8'), pw):
        token = 'secure'
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

    if token == "secure":
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
        if token == "secure":
            swimmers = db.get_all_from('swimmers')
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
        if token == "secure":
            swimmers = db.get_all_from('swimmers')
            return templates.TemplateResponse(
                request=request, name="admin/view_db.html", context = {"swimmers": swimmers}
            )
        else:
            return RedirectResponse(url="/admin", status_code=302)
