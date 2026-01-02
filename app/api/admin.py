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

@router.post("/users/{user_id}/qr")
def create_qr_user(user_id: int):
    qr_generator.generate_qr(
        data = str(user_id),
        user_id = int(user_id)
    )

    return RedirectResponse(
        url=f"/admin/users/{user_id}",
        status_code=303
    )

@router.get("/users/{user_id}/face")
def adding_face(user_id: int, request: Request):
    return templates.TemplateResponse(
        "get_face.html",
        {
            "request": request,
            "user_id": user_id
        }
    )

# @router.post("/users/{user_id}/face")
# def save_face(user_id: int, 
#     file: UploadFile = File(...), 
#     verifier: FaceVerification = Depends(get_face_verifier)):




@router.post("/users")
def add_user(name: str = Form(...)):
    new_user = user_service.add_user(name)
    
    return RedirectResponse(
        url="/admin/users",
        status_code=303
    )

