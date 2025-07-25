from fastapi import FastAPI, Request, Header, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder
from typing import Annotated, Union
import sqlite3
import random

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# Creates one if it doesn't exist
db = sqlite3.connect("swimmers.sql")
cursor = db.cursor()

# Create table if it doesn't exist
query = """
CREATE TABLE IF NOT EXISTS swimmers (
    id INTEGER PRIMARY KEY,
    todo_text TEXT NOT NULL,
    done BOOL DEFAULT FALSE
);
"""
cursor.execute(query)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request, hx_request: Annotated[Union[str, None], Header()] = None):
    if hx_request:
        return templates.TemplateResponse(
            request=request, name="htmx/index.html"
        )

    return templates.TemplateResponse(
        request=request, name="index.html"
    )

@app.get("/athletes", response_class=HTMLResponse)
async def athletes_page(request: Request, hx_request: Annotated[Union[str, None], Header()] = None):
    if hx_request:
        return templates.TemplateResponse(
            request=request, name="htmx/athletes.html"
        )
    return templates.TemplateResponse(
        request=request, name="athletes.html"
    )

@app.get("/records", response_class=HTMLResponse)
async def records_page(request: Request, hx_request: Annotated[Union[str, None], Header()] = None):
    if hx_request:
        return templates.TemplateResponse(
            request=request, name="htmx/records.html"
        )
    return templates.TemplateResponse(
        request=request, name="records.html"
    )

@app.get("/meets", response_class=HTMLResponse)
async def meets_page(request: Request, hx_request: Annotated[Union[str, None], Header()] = None):
    if hx_request:
        return templates.TemplateResponse(
            request=request, name="htmx/meets.html"
        )
    return templates.TemplateResponse(
        request=request, name="meets.html"
    )

@app.get("/admin", response_class=HTMLResponse)
async def admin_login(request: Request):
    return templates.TemplateResponse(
        request=request, name="admin.html"
    )

'''
@app.get("/todos", response_class=HTMLResponse)
async def list_todos(request: Request, hx_request: Annotated[Union[str, None], Header()] = None):
    query = "SELECT * FROM todos"
    cursor.execute(query)
    todos = cursor.fetchall()
    if hx_request:
        return templates.TemplateResponse(
            request=request, name="todos.html", context={"todos": todos}
        )
    return JSONResponse(content=jsonable_encoder(todos))

@app.post("/todos", response_class=HTMLResponse)
async def create_todo(request: Request, todo: Annotated[str, Form()]):
    query = f"INSERT INTO todos(todo_text) VALUES ('{todo}');"
    cursor.execute(query)
    cursor.execute("SELECT * FROM todos")
    todos = cursor.fetchall()
    return templates.TemplateResponse(
        request=request, name="todos.html", context={"todos": todos}
    )

@app.put("/todos/{todo_id}", response_class=HTMLResponse)
async def update_todo(request: Request, todo_id: str, text: Annotated[str, Form()]):
    query = f"""
    UPDATE todos
    SET todo_text = '{text}'
    WHERE id = {int(todo_id)};
    """

    cursor.execute(query)
    cursor.execute("SELECT * FROM todos")
    todos = cursor.fetchall()
    return templates.TemplateResponse(
        request=request, name="todos.html", context={"todos": todos}
    )

@app.post("/todos/{todo_id}/toggle", response_class=HTMLResponse)
async def toggle_todo(request: Request, todo_id: str):
    query = f"""
    UPDATE todos
    SET done = 1 - done
    WHERE id = {int(todo_id)};
    """
    cursor.execute(query)
    cursor.execute("SELECT * FROM todos")
    todos = cursor.fetchall()
    return templates.TemplateResponse(
        request=request, name="todos.html", context={"todos": todos}
    )


@app.post("/todos/{todo_id}/delete", response_class=HTMLResponse)
async def delete_todo(request: Request, todo_id: str):
    query = f"DELETE FROM todos WHERE id = {int(todo_id)};"
    cursor.execute(query)
    cursor.execute("SELECT * FROM todos")
    todos = cursor.fetchall()
    return templates.TemplateResponse(
        request=request, name="todos.html", context={"todos": todos}
    )
'''
