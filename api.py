from fastapi import APIRouter, File, Request, Header, UploadFile, Form, Security, HTTPException, status, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security.api_key import APIKeyCookie
from typing import Union, Annotated
from db import DB
import swimrankings
import base64
import imghdr

api_key_cookie = APIKeyCookie(name="access_token")

def get_api_key(api_key: str = Security(api_key_cookie)):
    if api_key != "secure":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    return api_key

router = APIRouter(prefix="/v1", dependencies=[Depends(get_api_key)])
templates = Jinja2Templates(directory="templates")

db = DB()
db.init_db()

@router.post("/remove-swimmer-photo", response_class=HTMLResponse)
async def api_remove_swimmer_photo(request: Request, photo_data: str = Form(...), hx_request: Annotated[Union[str, None], Header()] = None):
    if hx_request:
        photo_id, swimmer_id = photo_data.split(', ')

        if db.exists_in('swimmer_photos', f'id = {photo_id}'):
            db.delete_from('swimmer_photos', f'id = {photo_id}')
            db.commit()

            photos = db.get_all_from('swimmer_photos', sql_filter=f'swimmer_sql_id = {swimmer_id}')

            if photos:
                return templates.TemplateResponse(
                    request=request, name="htmx/admin_view_swimmer_photos.html", context={"photos": photos}
                )
        else:
            return RedirectResponse('/admin/view-db', status_code=302)




@router.post("/get-swimmer-photos", response_class=HTMLResponse)
async def api_get_swimmer_photos(request: Request, swimmer_id: int  = Form(...), hx_request: Annotated[Union[str, None], Header()] = None):
    if hx_request:
        if db.exists_in('swimmers', f'id = {swimmer_id}'):
            photos = db.get_all_from('swimmer_photos', sql_filter=f'swimmer_sql_id = {swimmer_id}')

            if photos:
                return templates.TemplateResponse(
                    request=request, name="htmx/admin_view_swimmer_photos.html", context={"photos": photos}
                )
        else:
            return RedirectResponse(
                '/admin/view-db', status_code=302
            )


@router.post("/add-swimmer-photo")
async def api_add_swimmer_photo(swimmer_id: int = Form(...), photo: UploadFile = File(...)):
    photo_bytes = await photo.read()
    photo_bytes_b64 = base64.b64encode(photo_bytes).decode('utf-8')
    photo_type = imghdr.what(None, h=photo_bytes)

    db.insert_into('swimmer_photos', 'data, img_type, swimmer_sql_id', f'{photo_bytes_b64, photo_type, swimmer_id}')
    db.commit()


@router.post("/add-swimmer", response_class=HTMLResponse)
async def api_add_swimmer(request: Request, full_name: Annotated[Union[str, None], Header(alias="HX-Prompt")] = None, hx_request: Annotated[Union[str, None], Header(alias="HX-Request")] = None):
    if hx_request:
        swimmer = swimrankings.get_swimmer(full_name)

        if swimmer:
            db.insert_into(
                'swimmers',
                'sw_id, birth_year, first_name, last_name, gender',
                f"{swimmer[0]},{swimmer[1]},'{swimmer[2]}','{swimmer[3]}',{swimmer[4]}"
            )

            db.commit()

            swimmers = db.get_all_from('swimmers')
            return templates.TemplateResponse(
                request=request, name="htmx/admin_view_db.html", context = {"swimmers": swimmers}
            )
        else:
            return RedirectResponse('/admin/view-db', status_code=302)

@router.post("/remove-swimmer", response_class=HTMLResponse)
async def api_remove_swimmer(request: Request, first_name: Annotated[Union[str, None], Header(alias="HX-Prompt")] = None, hx_request: Annotated[Union[str, None], Header(alias="HX-Request")] = None):
    if hx_request:
        db.delete_from('swimmers', f'first_name = {first_name}')
        db.commit()

        swimmers = db.get_all_from('swimmers')
        return templates.TemplateResponse(
            request=request, name="htmx/admin_view_db.html", context = {"swimmers": swimmers}
        )


@router.post("/sync-swimmers", response_class=HTMLResponse)
async def api_sync_swimmers(request: Request, hx_request: Annotated[Union[str, None], Header()] = None):
    swimmers = swimrankings.get_scwr_swimmers()
    if swimmers:
        for swimmer in swimmers:
            db_swimmer = db.get_all_from('swimmers', sql_filter=f'sw_id = {swimmer[0]}')
            if not db_swimmer:
                db.insert_into(
                    'swimmers',
                    'sw_id, birth_year, first_name, last_name, gender',
                    f"{swimmer[0]}, {swimmer[1]}, '{swimmer[2]}', '{swimmer[3]}', {swimmer[4]}"
                )
        
        sw_ids = ''
        for i in range(len(swimmers)):
            swimmer = swimmers[i]
            if i != len(swimmers) - 1:
                sw_ids += f'{swimmer[0]},'
                continue
            sw_ids += f'{swimmer[0]}'

        db.delete_from('swimmers', f'sw_id NOT IN ({sw_ids})')
        db.commit()

    if hx_request:
        swimmers = db.get_all_from('swimmers')
        return templates.TemplateResponse(
            request=request, name="htmx/admin_view_db.html", context = {"swimmers": swimmers}
        )
