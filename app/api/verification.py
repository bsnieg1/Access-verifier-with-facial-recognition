from fastapi import APIRouter, Request, File, HTTPException, UploadFile, Depends, Form
from fastapi.templating import Jinja2Templates
from ..models.verification import VerificationSession

from ..services import qr_scanner
from ..services import image_loader
from ..services import face_verification_singleton
from ..services import face_matcher
from ..services import face_manager

from datetime import datetime
import cv2
from pathlib import Path
from ..database import get_db, User, AccessLog
import uuid
from sqlalchemy.orm import Session

router = APIRouter()

APP_DIR = Path(__file__).parent.parent
templates = Jinja2Templates(directory=str(APP_DIR / "static" / "templates"))

SESSIONS = {}


@router.post("/start")
def start_verification(request: Request):
    session = VerificationSession()
    SESSIONS[session.id] = session

    return templates.TemplateResponse(
        "qr_scan.html",
        {
        "request": request,
        "session_id": session.id,
        "status": session.status
        }
    )

@router.post("/{session_id}/qr")
async def qr_scan(
    request: Request, 
    session_id: str, 
    file: UploadFile = File(...),
    entry_type: str = Form(default="WEJŚCIE"),
    db: Session = Depends(get_db)
):
    session = SESSIONS.get(session_id)
    if not session:
        return {"error": "Sesja nie znaleziona"}

    image = await image_loader.load_image_from_upload(file)
    qr_data = qr_scanner.scan_qr(image, draw_bbox=False)

    if not qr_data:
        return {"status": "QR_NOT_FOUND", "message": "Nie wykryto kodu QR"}
    
    user = db.query(User).filter(User.qr_code_id == qr_data).first()

    if not user:
        return {
            "status": "USER_NOT_FOUND",
            "message": "Nieznany kod QR (brak użytkownika w bazie)"
        }

    # Walidacja dla WEJŚCIA - sprawdzenie czy użytkownik już jest w fabryce
    if entry_type == "WEJŚCIE":
        last_entry = db.query(AccessLog).filter(
            AccessLog.user_id == user.id,
            AccessLog.entry_type == "WEJŚCIE",
            AccessLog.status == "SUCCESS"
        ).order_by(AccessLog.timestamp.desc()).first()
        
        last_exit = db.query(AccessLog).filter(
            AccessLog.user_id == user.id,
            AccessLog.entry_type == "WYJŚCIE",
            AccessLog.status == "SUCCESS"
        ).order_by(AccessLog.timestamp.desc()).first()
        
        # Jeśli ostatnie wejście jest nowsze niż ostatnie wyjście - już jest w fabryce
        if last_entry and (not last_exit or last_entry.timestamp > last_exit.timestamp):
            return {
                "status": "ALREADY_INSIDE",
                "message": "Jesteś już w fabryce! Najpierw musisz wyjść."
            }

    session.user_id = user.id
    session.entry_type = entry_type
    session.status = "WAITING_FOR_FACE"

    return {
        "status": "WAITING_FOR_FACE", 
        "user_id": user.id,
        "user_name": user.full_name,
        "entry_type": entry_type,
        "success": True,
    }

@router.post("/{session_id}/qr")
async def face_verify (session_id: str, file: UploadFile = File(...)):
    session = SESSIONS.get(session_id)

    if not session:

        return {
            "session_id": session_id,
            "error": "Sesja nie znaleziona (404)"
        }

    if session.status != "WAITING_FOR_FACE":
        return {
            "status": "INVALID_STATE",
            "expected": "WAITING_FOR_FACE",
            "error": "Nieprawidłowy stan sesji. Oczekiwano WAITING_FOR_FACE."
        }

    image = await image_loader.load_image_from_upload(file)

    user_id = session.user_id
    
@router.post("/{session_id}/face")
async def verify_face(
    session_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    session = SESSIONS.get(session_id)
    if not session or session.status not in ["WAITING_FOR_FACE", "ACCESS_DENIED"]:
        return {"error": "Nieprawidłowy stan sesji"}

    image = await image_loader.load_image_from_upload(file)
    user_id = session.user_id

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
         return {"status": "USER_NOT_FOUND"}

    if not user.face_image_path or not face_manager.has_face(user.id):
        session.status = "ACCESS_DENIED"
        return {
            "status": "ACCESS_DENIED", 
            "message": "Błąd: Brak wzorca twarzy w systemie. Skontaktuj się z administratorem."
        }

    is_match = face_matcher.verify_face_for_user(
        image,
        user_id=user.id,
        verifier=face_verification_singleton.face_verifier,
        threshold=0.6
    )

    log_dir = Path("data/logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    status_str = "SUCCESS" if is_match else "FAILED"
    
    filename = f"log_{status_str}_u{user_id}_{timestamp_str}.jpg"
    log_path = log_dir / filename
    
    cv2.imwrite(str(log_path), image)

    entry_type = getattr(session, 'entry_type', 'WEJŚCIE')
    
    # Obliczanie czasu spędzenia w fabryce dla wyjścia
    duration_seconds = None
    if entry_type == "WYJŚCIE" and status_str == "SUCCESS":
        # Szukamy ostatniego WEJŚCIA tego użytkownika
        last_entry = db.query(AccessLog).filter(
            AccessLog.user_id == user_id,
            AccessLog.entry_type == "WEJŚCIE",
            AccessLog.status == "SUCCESS"
        ).order_by(AccessLog.timestamp.desc()).first()
        
        # Szukamy ostatniego WYJŚCIA tego użytkownika
        last_exit = db.query(AccessLog).filter(
            AccessLog.user_id == user_id,
            AccessLog.entry_type == "WYJŚCIE",
            AccessLog.status == "SUCCESS"
        ).order_by(AccessLog.timestamp.desc()).first()
        
        # Sprawdzenie czy można wyjść (musi być wejście i być nowsze niż ostatnie wyjście)
        if not last_entry or (last_exit and last_exit.timestamp > last_entry.timestamp):
            # Brak wejścia lub ostatni wpis to wyjście - nie można wyjść
            session.status = "ACCESS_DENIED"
            return {
                "status": "ACCESS_DENIED", 
                "message": "Nie możesz wyjść z fabryki, ponieważ nie masz zarejestrowanego wejścia!"
            }
        
        now = datetime.utcnow()
        duration = now - last_entry.timestamp
        duration_seconds = int(duration.total_seconds())
    
    new_log = AccessLog(
        user_id=user_id,
        status=status_str,
        entry_type=entry_type,
        captured_image_path=f"data/logs/{filename}",
        duration_seconds=duration_seconds
    )
    db.add(new_log)
    db.commit()

    if not is_match:
        session.status = "ACCESS_DENIED"
        return {
            "status": "ACCESS_DENIED", 
            "message": "Twarz nie pasuje do wzorca. Spróbuj ponownie."
        }

    session.status = "ACCESS_GRANTED"
    return {
        "status": "ACCESS_GRANTED",
        "redirect_url": f"/verification/{session_id}/success"
    }

@router.get("/{session_id}/success")
def verification_success(
    request: Request, 
    session_id: str, 
    db: Session = Depends(get_db) 
):
    session = SESSIONS.get(session_id)

    if not session or session.status != "ACCESS_GRANTED":
        return RedirectResponse(url="/", status_code=303)

    user = db.query(User).filter(User.id == session.user_id).first()

    if not user:
        return RedirectResponse(url="/", status_code=303)

    # Pobierz ostatni log użytkownika aby pokazać czas spędzony
    last_log = db.query(AccessLog).filter(
        AccessLog.user_id == session.user_id
    ).order_by(AccessLog.timestamp.desc()).first()
    
    entry_type = getattr(session, 'entry_type', 'WEJŚCIE')
    duration_seconds = last_log.duration_seconds if last_log else None

    return templates.TemplateResponse(
        "success.html",
        {
            "request": request, 
            "user": user,
            "session_id": session_id,
            "entry_type": entry_type,
            "duration_seconds": duration_seconds
        }
    )