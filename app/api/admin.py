from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from services import user_service
from services import qr_generator
from services import qr_scanner

router = APIRouter()

templates = Jinja2Templates(directory="templates")



@router.get("/users")
def render_users(request: Request):
    
    users = user_service.get_users()

    return templates.TemplateResponse(
        "admin_panel.html",
        {"request": request, "users": users}
    )

@router.get("/users/new")
def create_user_form(request: Request):
    return templates.TemplateResponse(
        "new_user.html",
        {"request": request}
    )

@router.get("/users/{user_id}")
def render_user_detail(request: Request, user_id: int):
    
    user = user_service.get_user(user_id)

    return templates.TemplateResponse(
        "specific_user.html",
        {"request": request, "user": user}
    )

@router.post("/users")
def add_user(name: str = Form(...)):
    new_user = user_service.add_user(name)
    
    return RedirectResponse(
        url="/admin/users",
        status_code=303
    )

