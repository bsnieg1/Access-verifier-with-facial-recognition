from fastapi import Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext
from dotenv import load_dotenv
import os
import hashlib
import secrets
from functools import wraps

load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

templates = Jinja2Templates(directory="templates")  

def verify_password(plain_password: str):
    stored_value = os.getenv("ADMIN_PASSWORD_HASH")
    
    if not stored_value or ":" not in stored_value:
        return False

    salt_hex, hash_hex = stored_value.split(":")
    new_hash = hashlib.pbkdf2_hmac(
        'sha256', 
        plain_password.strip().encode('utf-8'), 
        bytes.fromhex(salt_hex), 
        100000
    )
    
    result = new_hash.hex() == hash_hex
    print(f"DEBUG: Wynik porównania: {result}")
    return result

async def require_admin(request: Request):
    if not request.session.get("admin_logged_in"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Brak autoryzacji"
        )
    return True