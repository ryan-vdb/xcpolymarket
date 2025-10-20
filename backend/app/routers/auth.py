from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from ..db import conn
from ..auth import hash_password, verify_password, create_token, get_current_username

router = APIRouter()

class RegisterReq(BaseModel):
    username: str = Field(min_length=3, max_length=32)
    password: str = Field(min_length=6, max_length=128)
    starting_points: int = Field(1000, ge=0)

class LoginReq(BaseModel):
    username: str
    password: str

@router.post("/register")
def register(req: RegisterReq):
    with conn() as c:
        row = c.execute("SELECT username FROM users WHERE username=?", (req.username,)).fetchone()
        if row:
            raise HTTPException(400, "Username already taken")
        c.execute(
            "INSERT INTO users(username, balance_cents, password_hash) VALUES (?, ?, ?)",
            (req.username, req.starting_points * 100, hash_password(req.password)),
        )
    token = create_token(req.username)
    return {"access_token": token, "token_type": "bearer", "username": req.username}

@router.post("/login")
def login(req: LoginReq):
    with conn() as c:
        row = c.execute(
            "SELECT username, password_hash FROM users WHERE username=?",
            (req.username,),
        ).fetchone()
        if not row or not row["password_hash"] or not verify_password(req.password, row["password_hash"]):
            raise HTTPException(401, "Invalid credentials")
    token = create_token(req.username)
    return {"access_token": token, "token_type": "bearer", "username": req.username}

@router.get("/me")
def me(username: str = get_current_username):
    return {"username": username}