from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
from database import init_db
import os

from api.verification import router as verification_router
from api.admin import router as admin_panel_router

load_dotenv()

app = FastAPI(title="Factory Access System")

init_db()

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY"),
    max_age=3600
)

templates = Jinja2Templates(directory="templates")

os.makedirs("data/qr_codes", exist_ok=True)
os.makedirs("data/faces", exist_ok=True)
os.makedirs("data/logs", exist_ok=True)

app.mount("/data", StaticFiles(directory="data"), name="data")

@app.get("/")
def index(request: Request):
    request.session.clear()

    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )


app.include_router(
    verification_router,
    prefix="/verification",
    tags=["verification"]
)

app.include_router(
    admin_panel_router,
    prefix="/admin",
    tags=["admin_panel"]
)


