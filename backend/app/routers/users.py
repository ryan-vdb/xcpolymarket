from fastapi import APIRouter, HTTPException, Header
from ..db import conn
from ..config import ADMIN_TOKEN
from ..schemas.users import UserCreate, UserOut

router = APIRouter()

@router.post("", response_model=UserOut)
def create_user(req: UserCreate, x_admin_token: str = Header(default="")):
    if x_admin_token != ADMIN_TOKEN:
        raise HTTPException(401, "admin token required")
    with conn() as c:
        try:
            c.execute(
                "INSERT INTO users(username, balance_cents) VALUES (?, ?)",
                (req.username, req.starting_points * 100)
            )
        except Exception as e:
            raise HTTPException(400, f"user create failed: {e}")
        row = c.execute("SELECT username, balance_cents FROM users WHERE username=?",
                        (req.username,)).fetchone()
    return UserOut(username=row["username"], balance_points=row["balance_cents"]/100.0)

@router.get("/{username}", response_model=UserOut)
def get_user(username: str):
    with conn() as c:
        row = c.execute("SELECT username, balance_cents FROM users WHERE username=?",
                        (username,)).fetchone()
        if not row:
            raise HTTPException(404, "user not found")
    return UserOut(username=row["username"], balance_points=row["balance_cents"]/100.0)