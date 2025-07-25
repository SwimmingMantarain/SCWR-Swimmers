from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from routes.pages import router as pages_router
from api import router as api_router

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

# Mount routers
app.include_router(pages_router)
app.include_router(api_router)

templates = Jinja2Templates(directory="templates")

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
