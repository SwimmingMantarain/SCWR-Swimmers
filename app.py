from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from pages import router as pages_router
from api import router as api_router
from admin import router as admin_router

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

# Mount routers
app.include_router(pages_router)
app.include_router(api_router)
app.include_router(admin_router)
