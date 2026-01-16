from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
import os

from api.verification import router as verification_router
from api.admin import router as admin_panel_router

load_dotenv()

app = FastAPI(title="Factory Access System")

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY"),
    max_age=3600
)

templates = Jinja2Templates(directory="templates")

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

os.makedirs("data/qr_codes", exist_ok=True)
os.makedirs("data/faces", exist_ok=True)

app.mount("/qr_codes", StaticFiles(directory="data/qr_codes"), name="qr_codes")
app.mount("/faces", StaticFiles(directory="data/faces"), name="faces")
