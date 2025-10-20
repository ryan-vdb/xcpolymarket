from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt  # use python-jose
from passlib.hash import bcrypt
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from .db import conn

JWT_SECRET = "dev-secret-change-me"
JWT_ALG = "HS256"
JWT_EXP_MIN = 60 * 24 * 7  # 7 days

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def hash_password(pw: str) -> str:
    return bcrypt.hash(pw)

def verify_password(pw: str, hashed: str) -> bool:
    return bcrypt.verify(pw, hashed)

def create_token(username: str) -> str:
    exp_ts = int((datetime.now(timezone.utc) + timedelta(minutes=JWT_EXP_MIN)).timestamp())
    payload = {"sub": username, "exp": exp_ts}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)

def get_current_username(token: str = Depends(oauth2_scheme)) -> str:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        username = payload.get("sub")
    except Exception:
        raise HTTPException(401, "Invalid token")
    if not username:
        raise HTTPException(401, "Invalid token")
    return username  # <-- no DB lookup here