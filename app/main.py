from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
import os
from pathlib import Path

from .database import init_db
from .api.verification import router as verification_router
from .api.admin import router as admin_panel_router

load_dotenv()

app = FastAPI(title="Factory Access System")

init_db()

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY"),
    max_age=3600
)

BASE_DIR = Path(__file__).parent.parent
APP_DIR = Path(__file__).parent
TEMPLATES_DIR = APP_DIR / "static" / "templates"
STATIC_DIR = APP_DIR / "static"

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

os.makedirs(BASE_DIR / "data" / "qr_codes", exist_ok=True)
os.makedirs(BASE_DIR / "data" / "faces", exist_ok=True)
os.makedirs(BASE_DIR / "data" / "logs", exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.mount("/data", StaticFiles(directory=str(BASE_DIR / "data")), name="data")

@app.get("/")
def index(request: Request):
    request.session.clear()

    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )

app.include_router(verification_router, prefix="/verification", tags=["verification"])
app.include_router(admin_panel_router, prefix="/admin", tags=["admin"])


