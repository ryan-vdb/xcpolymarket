from datetime import datetime, timedelta
from typing import Optional
import jwt  # PyJWT
from passlib.hash import bcrypt
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from .db import conn

JWT_SECRET = "dev-secret-change-me"
JWT_ALG = "HS256"
JWT_EXP_MIN = 60 * 24 * 7  # 7 days

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def hash_password(pw: str) -> str:
    return bcrypt.hash(pw)

def verify_password(pw: str, hashed: str) -> bool:
    return bcrypt.verify(pw, hashed)

def create_token(username: str) -> str:
    exp = datetime.utcnow() + timedelta(minutes=JWT_EXP_MIN)
    return jwt.encode({"sub": username, "exp": exp}, JWT_SECRET, algorithm=JWT_ALG)

def get_current_username(token: str = Depends(oauth2_scheme)) -> str:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        username: Optional[str] = payload.get("sub")
    except jwt.PyJWTError:
        raise HTTPException(401, "Invalid token")
    if not username:
        raise HTTPException(401, "Invalid token")
    with conn() as c:
        row = c.execute("SELECT username FROM users WHERE username=?", (username,)).fetchone()
        if not row:
            raise HTTPException(401, "User not found")
    return username