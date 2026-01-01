from fastapi import APIRouter
from models.verification import VerificationSession

router = APIRouter()

# tymczasowy storage w pamięci
SESSIONS = {}


@router.post("/start")
def start_verification():
    session = VerificationSession()
    SESSIONS[session.id] = session

    return {
        "session_id": session.id,
        "status": session.status
    }
