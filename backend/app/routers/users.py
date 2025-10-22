# backend/app/routers/users.py
from fastapi import APIRouter, HTTPException, Header, Depends
from ..db import conn, DB_PATH
from ..config import ADMIN_TOKEN
from ..schemas.users import UserCreate, UserOut
from ..auth import get_current_username

router = APIRouter()

# --- Token-based conveniences (PUT THESE FIRST!) ---

# GET /users/me
@router.get("/me", response_model=UserOut)
def get_me(username: str = Depends(get_current_username)):
    with conn() as c:
        row = c.execute(
            "SELECT username, balance_cents FROM users WHERE username=?",
            (username,)
        ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail=f"user not found (username={username}, db={DB_PATH})")
    return UserOut(username=row["username"], balance_points=row["balance_cents"] / 100.0)

# GET /users/me/bets
@router.get("/me/bets")
def get_my_bets(username: str = Depends(get_current_username)):
    with conn() as c:
        rows = c.execute(
            """
            SELECT b.market_id, b.side, b.amount_cents, b.created_at,
                   m.question, m.closes_at, m.open
            FROM bets b
            LEFT JOIN markets m ON m.id = b.market_id
            WHERE b.username=?
            ORDER BY b.created_at DESC
            """,
            (username,),
        ).fetchall()
    return [
        {
            "market_id": r["market_id"],
            "question": r["question"],
            "closes_at": r["closes_at"],
            "open": bool(r["open"]),
            "side": r["side"],
            "spend_points": r["amount_cents"] / 100.0,
            "created_at": r["created_at"],
        }
        for r in rows
    ]

# --- Admin seed/create ---

@router.post("", response_model=UserOut)
def create_user(req: UserCreate, x_admin_token: str = Header(default="")):
    if x_admin_token != ADMIN_TOKEN:
        raise HTTPException(401, "admin token required")
    with conn() as c:
        try:
            c.execute(
                "INSERT INTO users(username, balance_cents) VALUES (?, ?)",
                (req.username, req.starting_points * 100),
            )
        except Exception as e:
            raise HTTPException(400, f"user create failed: {e}")
        row = c.execute(
            "SELECT username, balance_cents FROM users WHERE username=?",
            (req.username,),
        ).fetchone()
    return UserOut(username=row["username"], balance_points=row["balance_cents"] / 100.0)

# --- Named user (KEEP THIS LAST) ---

@router.get("/{username}", response_model=UserOut)
def get_user(username: str):
    with conn() as c:
        row = c.execute(
            "SELECT username, balance_cents FROM users WHERE username=?",
            (username,),
        ).fetchone()
        if not row:
            raise HTTPException(404, "user not found")
    return UserOut(username=row["username"], balance_points=row["balance_cents"] / 100.0)