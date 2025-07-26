from fastapi import APIRouter, Request, Header, Cookie, HTTPException, Depends
from fastapi import templating
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Annotated, Union

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
    if hx_request:
        return templates.TemplateResponse(
            request=request, name="htmx/athletes.html"
        )
    return templates.TemplateResponse(
        request=request, name="athletes.html"
    )

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
