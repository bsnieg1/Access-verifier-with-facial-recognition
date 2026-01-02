from fastapi import APIRouter, Request, File, HTTPException, UploadFile
from fastapi.templating import Jinja2Templates
from models.verification import VerificationSession

from services import qr_scanner
from services import image_loader
from services import user_service

router = APIRouter()

templates = Jinja2Templates(directory="templates")

# tymczasowy storage w pamięci
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
async def qr_scan(request: Request, session_id: str, file: UploadFile = File(...)):
    session = SESSIONS.get(session_id)

    if not session:
        return {
            "session_id": session_id,
            "error": "Sesja nie znaleziona (404)"
        }
        

    if session.status != "WAITING_FOR_QR":
        return {
            "status": "INVALID_STATE",
            "expected": "WAITING_FOR_QR",
            "error": "Nieprawidłowy stan sesji. Oczekiwano WAITING_FOR_QR."
        }
        
    
    image = await image_loader.load_image_from_upload(file)

    qr_data = qr_scanner.scan_qr(image, draw_bbox=False)

    if not qr_data:
        return {
            "status": "QR_NOT_FOUND",
            "message": "Nie wykryto kodu QR",
            "error": "Nie wykryto kodu QR"
        }
        
    try:
        user_id = int(qr_data)
    except ValueError:
        return {
            "status": "INVALID_QR",
            "message": "QR nie zawiera poprawnego user_id",
            "error": "QR nie zawiera poprawnego user_id"
        }

    if not user_service.get_user(user_id):
        return {
            "status": "USER_NOT_FOUND",
            "error": "Użytkownik nie znaleziony"
        }

    session.user_id = user_id
    session.status = "WAITING_FOR_FACE"

    return {
        "status": "QR_OK",
        "user_id": user_id,
        "next_step": "FACE_VERIFICATION",
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
    
