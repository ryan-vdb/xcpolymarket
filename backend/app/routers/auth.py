# backend/app/routers/auth.py
from fastapi import APIRouter, HTTPException, Header
from jose import jwt
from pydantic import BaseModel, Field
from ..db import conn
from ..auth import hash_password, verify_password, create_token, JWT_SECRET, JWT_ALG  # uses your PyJWT helpers

router = APIRouter()

class RegisterReq(BaseModel):
    username: str = Field(min_length=3, max_length=32)
    password: str = Field(min_length=3, max_length=128)
    starting_points: int = Field(1000, ge=0)

class LoginReq(BaseModel):
    username: str
    password: str

@router.post("/register")
def register(data: RegisterReq):
    u = data.username.strip()
    if not u:
        raise HTTPException(400, "username required")
    start_cents = int(round(data.starting_points * 100))
    pw_hash = hash_password(data.password)

    with conn() as c:
        exists = c.execute("SELECT 1 FROM users WHERE username=?", (u,)).fetchone()
        if exists:
            raise HTTPException(400, "username already exists")

        # matches your schema: users(username, balance_cents, password_hash)
        c.execute(
            "INSERT INTO users (username, balance_cents, password_hash) VALUES (?, ?, ?)",
            (u, start_cents, pw_hash),
        )

    # auto-login right after register
    return {
        "access_token": create_token(u),
        "token_type": "bearer",
        "username": u,
    }

@router.post("/login")
def login(data: LoginReq):
    try:
        u = data.username.strip()
        pw = data.password
        # fetch row
        with conn() as c:
            row = c.execute(
                "SELECT username, password_hash FROM users WHERE username=?",
                (u,),
            ).fetchone()
        if not row:
            raise HTTPException(401, "invalid credentials (no such user)")
        if not row["password_hash"]:
            raise HTTPException(401, "invalid credentials (no password set)")
        # verify password
        if not verify_password(pw, row["password_hash"]):
            raise HTTPException(401, "invalid credentials (bad password)")
        # success -> issue token
        return {
            "access_token": create_token(u),
            "token_type": "bearer",
            "username": u,
        }
    except HTTPException:
        raise
    except Exception as e:
        # TEMP: surface the real error so we stop guessing
        raise HTTPException(500, f"login crash: {type(e).__name__}: {e}")


from fastapi import Header


@router.get("/whoami")
def whoami(authorization: str = Header(default="")):
    if not authorization.startswith("Bearer "):
        return {"ok": False, "error": "no bearer token"}
    token = authorization.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        return {"ok": True, "payload": payload}
    except Exception as e:
        return {"ok": False, "error": str(e)}
