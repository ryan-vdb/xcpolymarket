from fastapi import APIRouter, HTTPException, Header, Depends
from ..db import conn, DB_PATH
from ..config import ADMIN_TOKEN
from ..schemas.users import UserCreate, UserOut
from ..auth import get_current_username

router = APIRouter()

# GET /users/leaderboard  — list all users by balance (desc)
@router.get("/leaderboard")
def leaderboard():
    with conn() as c:
        rows = c.execute(
            "SELECT username, balance_cents FROM users ORDER BY balance_cents DESC"
        ).fetchall()
    return [
        {"username": r["username"], "balance_points": r["balance_cents"] / 100.0}
        for r in rows
    ]

# POST /users  (admin-only seed/create user)
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


# --- Token-based conveniences ---

# GET /users/me
@router.get("/me", response_model=UserOut)
def get_me(username: str = Depends(get_current_username)):
    with conn() as c:
        row = c.execute(
            "SELECT username, balance_cents FROM users WHERE username=?",
            (username,)
        ).fetchone()
    if not row:
        # include diagnostics so we see what the server actually used
        raise HTTPException(status_code=404, detail=f"user not found (username={username}, db={DB_PATH})")
    return UserOut(username=row["username"], balance_points=row["balance_cents"] / 100.0)

# GET /users/me/bets  (optional helper for the Account page)
@router.get("/me/bets")
def get_my_bets(username: str = Depends(get_current_username)):
    with conn() as c:
        rows = c.execute(
            """
            SELECT b.market_id, b.side, b.amount_cents,
                   m.question, m.closes_at, m.open,
                   m.s_yes_cents, m.s_no_cents
            FROM bets b
            JOIN markets m ON m.id = b.market_id
            WHERE b.username=?
            ORDER BY b.created_at DESC
            """,
            (username,),
        ).fetchall()
    out = []
    for r in rows:
        out.append({
            "market_id": r["market_id"],
            "question": r["question"],
            "closes_at": r["closes_at"],
            "open": bool(r["open"]),
            "side": r["side"],
            "amount_points": r["amount_cents"] / 100.0,
            "yes_pool_points": r["s_yes_cents"] / 100.0,
            "no_pool_points":  r["s_no_cents"]  / 100.0,
        })
    return out

@router.get("/me_raw")
def me_raw(username: str = Depends(get_current_username)):
    from ..db import DB_PATH
    with conn() as c:
        row = c.execute(
            "SELECT username, balance_cents, (password_hash IS NOT NULL) AS has_hash "
            "FROM users WHERE username=?",
            (username,)
        ).fetchone()
    return {
        "username_from_token": username,
        "db_path": DB_PATH,
        "row": dict(row) if row else None
    }

# GET /users/{username}
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
