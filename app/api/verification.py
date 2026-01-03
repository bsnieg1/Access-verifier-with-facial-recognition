from fastapi import APIRouter, Request, File, HTTPException, UploadFile
from fastapi.templating import Jinja2Templates
from models.verification import VerificationSession

from services import qr_scanner
from services import image_loader
from services import user_service
from services import face_verification_singleton
from services import face_matcher


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
    
@router.post("/{session_id}/face")
async def verify_face(
    session_id: str,
    file: UploadFile = File(...)
):
    session = SESSIONS.get(session_id)

    if not session:
        return {
            "session_id": session_id,
            "error": "Sesja nie znaleziona (404)"
        }

    if session.status not in ["WAITING_FOR_FACE", "ACCESS DENIED"]:
        return {
            "status": "INVALID_STATE",
            "expected": "WAITING_FOR_FACE",
            "error": "Nieprawidłowy stan sesji. Oczekiwano WAITING_FOR_FACE."
        }

    image = await image_loader.load_image_from_upload(file)

    user_id = session.user_id

    user = user_service.get_user(user_id)
    if not user:
        return {"status": "USER_NOT_FOUND"}

    is_match = face_matcher.verify_face_for_user(
        image,
        user_id=user_id,  
        verifier=face_verification_singleton.face_verifier,
        threshold=0.6
    )

    if not is_match:
        session.status = "ACCESS_DENIED"
        return {"status": "ACCESS_DENIED"}

    session.status = "ACCESS_GRANTED"
    return {
        "status": "ACCESS_GRANTED",
        "user_id": user_id
    }

@router.get("/{session_id}/success")
def verification_success(request: Request, session_id: str):

    session = SESSIONS.get(session_id)


    if not session or session.status != "ACCESS_GRANTED":
        return RedirectResponse(url="/", status_code=303)

    user = user_service.get_user(session.user_id)

    return templates.TemplateResponse(
        "success.html",
        {
            "request": Request,
            "user": user,
            "session_id": session_id
        }
    )
    