from fastapi import APIRouter, Request, Form, File, UploadFile, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from services import user_service
from services import qr_generator
from services import qr_scanner
from services import face_manager
from services import image_loader

from utils import auth
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

templates = Jinja2Templates(directory="templates")



@router.get("/users")
def render_users(request: Request, _ = Depends(auth.require_admin)):
    
    users = user_service.get_users()

    return templates.TemplateResponse(
        "admin_panel.html",
        {"request": request, "users": users}
    )

@router.get("/users/new")
def create_user_form(request: Request, _ = Depends(auth.require_admin)):
    return templates.TemplateResponse(
        "new_user.html",
        {"request": request}
    )

@router.get("/users/{user_id}")
def render_user_detail(request: Request, user_id: int, _ = Depends(auth.require_admin)):
    user = user_service.get_user(user_id)

    return templates.TemplateResponse(
        "specific_user.html",
        {"request": request, "user": user}
    )

@router.post("/users/{user_id}/qr")
def create_qr_user(user_id: int, _ = Depends(auth.require_admin)):
    qr_generator.generate_qr(
        data = str(user_id),
        user_id = int(user_id)
    )

    return RedirectResponse(
        url=f"/admin/users/{user_id}",
        status_code=303
    )

@router.get("/users/{user_id}/face")
def adding_face(user_id: int, request: Request, _ = Depends(auth.require_admin)):
    return templates.TemplateResponse(
        "get_face.html",
        {
            "request": request,
            "user_id": user_id
        }
    )

@router.post("/users/{user_id}/face")
async def save_face(user_id: int, file: UploadFile = File(...), _ = Depends(auth.require_admin)):
    
    try:
        image = await image_loader.load_image_from_upload(file)

        face_manager.save_face_image(
            image=image,
            user_id = user_id
        )
        return RedirectResponse(
                url=f"/admin/users/{user_id}",
                status_code=303
            )
    except Exception as e:
        print(f"❌ Błąd podczas zapisywania zdjęcia: {e}")
        return RedirectResponse(
            url=f"/admin/users/{user_id}",
            status_code=303
        )


@router.post("/users")
def add_user(name: str = Form(...), _ = Depends(auth.require_admin)):
    new_user = user_service.add_user(name)
    
    return RedirectResponse(
        url="/admin/users",
        status_code=303
    )

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {"request": request, 
        "message": request.query_params.get("message", "")}
    )

@router.post("/login")
async def login_post(request: Request, password: str = Form(...)):
    if auth.verify_password(password):
        request.session["admin_logged_in"] = True
        return RedirectResponse(url="/admin/users", status_code=303)
    else:
        return RedirectResponse(url="/admin/login?message=Błędne hasło", status_code=303)

@router.get("/logout")
async def logout(request: Request):
    request.session.pop("admin_logged_in", None)
    return RedirectResponse(url="/admin/login", status_code=303)