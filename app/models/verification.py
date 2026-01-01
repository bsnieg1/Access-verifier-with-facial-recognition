from enum import Enum
from uuid import uuid4
from datetime import datetime


class VerificationStatus(str, Enum):
    NEW = "NEW"
    WAITING_FOR_QR = "WAITING_FOR_QR"
    WAITING_FOR_FACE = "WAITING_FOR_FACE"
    VERIFIED = "VERIFIED"
    FAILED = "FAILED"


class VerificationSession:
    def __init__(self):
        self.id = str(uuid4())
        self.status = VerificationStatus.WAITING_FOR_QR
        self.user_id = None
        self.created_at = datetime.utcnow()
