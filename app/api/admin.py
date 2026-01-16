from fastapi import APIRouter, Request, Form, File, UploadFile, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

# from services import user_service
from services import qr_generator
from services import qr_scanner
from services import face_manager
from services import image_loader
from database import get_db, User, AccessLog
from sqlalchemy.orm import Session
from typing import Optional

import qrcode
import shutil
import os
import uuid

from utils import auth
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

templates = Jinja2Templates(directory="templates")


# USERS-------------------
@router.get("/users")
async def list_users(request: Request, db: Session = Depends(get_db), _ = Depends(auth.require_admin)):
    users = db.query(User).all()
    return templates.TemplateResponse("admin_panel.html", {"request": request, "users": users})

@router.get("/users/new")
def create_user_form(request: Request, _ = Depends(auth.require_admin)):
    return templates.TemplateResponse(
        "new_user.html",
        {"request": request}
    )

@router.post("/users/new")
async def add_user(
    name: str = Form(...),
    db: Session = Depends(get_db),
    _ = Depends(auth.require_admin)
):
    user_uuid = str(uuid.uuid4())
    new_user = User(full_name=name, qr_code_id=user_uuid,face_image_path=None, qr_image_path=None)
    db.add(new_user)
    db.commit()
    
    return RedirectResponse(url="/admin/users", status_code=303)

@router.post("/users/{user_id}/delete")
async def delete_user(
    user_id: int, 
    db: Session = Depends(get_db), 
    _ = Depends(auth.require_admin)
):
    user = db.query(User).filter(User.id == user_id).first()
    
    if user:

        paths_to_check = []
        if user.face_image_path:
            paths_to_check.append(f"{user.face_image_path}")
        if user.qr_image_path:
            paths_to_check.append(f"{user.qr_image_path}")

        for path in paths_to_check:

            full_path = path if path.startswith("app/") else f"app/{path}"
            
            if os.path.exists(full_path):
                try:
                    os.remove(full_path)
                    print(f"Usunięto plik: {full_path}")
                except Exception as e:
                    print(f"Błąd przy usuwaniu pliku {full_path}: {e}")
            else:
                alternative_path = path.replace("app/", "") if path.startswith("app/") else path
                if os.path.exists(alternative_path):
                    os.remove(alternative_path)

        db.delete(user)
        db.commit()
        print(f"Użytkownik {user_id} usunięty z bazy.")

    return RedirectResponse(url="/admin/users", status_code=303)

@router.get("/users/{user_id}")
def render_user_detail(
    request: Request, 
    user_id: int, 
    db: Session = Depends(get_db), 
    _ = Depends(auth.require_admin)
):
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        return HTMLResponse("Użytkownik nie istnieje", status_code=404)

    return templates.TemplateResponse(
        "specific_user.html",
        {"request": request, "user": user}
    )

# QR-------------------
@router.post("/users/{user_id}/qr/create")
def create_qr_user(
    user_id: int, 
    db: Session = Depends(get_db), 
    _ = Depends(auth.require_admin)
):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        qr_path = qr_generator.generate_qr(data=user.qr_code_id, user_id=user.id)
        
        user.qr_image_path = qr_path
        db.commit()

    return RedirectResponse(url=f"/admin/users/{user_id}", status_code=303)

@router.post("/users/{user_id}/qr/delete")
async def delete_qr_code(
    user_id: int, 
    db: Session = Depends(get_db), 
    _ = Depends(auth.require_admin)
):
    user = db.query(User).filter(User.id == user_id).first()
    
    if user and user.qr_image_path:
        full_path = f"app/{user.qr_image_path}" if not user.qr_image_path.startswith("app/") else user.qr_image_path
        
        if os.path.exists(full_path):
            try:
                os.remove(full_path)
            except Exception as e:
                print(f"Błąd przy usuwaniu pliku QR: {e}")
        
        user.qr_image_path = None
        db.commit()

    return RedirectResponse(url=f"/admin/users/{user_id}", status_code=303)

# FACE-------------------
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
async def save_face(
    user_id: int, 
    file: UploadFile = File(...), 
    db: Session = Depends(get_db),
    _ = Depends(auth.require_admin)
):
    try:
        image = await image_loader.load_image_from_upload(file)

        saved_path = face_manager.save_face_image(image=image, user_id=user_id)

        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.face_image_path = str(saved_path).replace("\\", "/")
            db.commit()

        return {"status": "success"}
    except Exception as e:
        print(f" Błąd zapisu twarzy: {e}")
        return {"status": "error", "message": str(e)}

@router.post("/users/{user_id}/face/delete")
async def delete_face(
    user_id: int, 
    db: Session = Depends(get_db), 
    _ = Depends(auth.require_admin)
):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        face_manager.delete_user_faces(user_id)
        
        user.face_image_path = None
        db.commit()

    return RedirectResponse(url=f"/admin/users/{user_id}", status_code=303)

# @router.post("/users")
# def add_user(name: str = Form(...), _ = Depends(auth.require_admin)):
#     new_user = user_service.add_user(name)
    
#     return RedirectResponse(
#         url="/admin/users",
#         status_code=303
#     )

# LOGIN-------------------
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

#LOGS-------
@router.get("/logs")
def get_logs(request: Request, db: Session = Depends(get_db), _ = Depends(auth.require_admin)):
    all_logs = db.query(AccessLog).order_by(AccessLog.timestamp.desc()).all()
    return templates.TemplateResponse("logs.html", {"request": request, "logs": all_logs})