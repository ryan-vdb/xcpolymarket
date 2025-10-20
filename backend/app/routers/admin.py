from fastapi import APIRouter, HTTPException, Header, Query
from typing import Optional
from ..db import conn
from ..config import ADMIN_TOKEN
from ..schemas.markets import SettleReq
from ..logic import odds, implied_payout_per1

router = APIRouter()

def _require_admin(token: Optional[str]):
    if token != ADMIN_TOKEN:
        raise HTTPException(401, "admin token required")

# --------- LIST VIEWS ---------

@router.get("/users")
def list_users(x_admin_token: Optional[str] = Header(default=None, alias="X-Admin-Token")):
    _require_admin(x_admin_token)
    with conn() as c:
        rows = c.execute(
            "SELECT username, balance_cents FROM users ORDER BY username ASC"
        ).fetchall()
    return [
        {
            "username": r["username"],
            "balance_points": r["balance_cents"] / 100.0,
        }
        for r in rows
    ]

@router.get("/markets")
def list_markets_admin(
    x_admin_token: Optional[str] = Header(default=None, alias="X-Admin-Token"),
    status: Optional[str] = Query(default=None)  # open | closed | None
):
    _require_admin(x_admin_token)

    where = ""
    if status == "open":
        where = "WHERE open=1"
    elif status == "closed":
        where = "WHERE open=0"

    with conn() as c:
        rows = c.execute(
            f"SELECT id, question, closes_at, open, s_yes_cents, s_no_cents "
            f"FROM markets {where} ORDER BY closes_at ASC"
        ).fetchall()

    out = []
    for r in rows:
        o = odds(r["s_yes_cents"], r["s_no_cents"])
        p = implied_payout_per1(r["s_yes_cents"], r["s_no_cents"])
        out.append({
            "id": r["id"],
            "question": r["question"],
            "closes_at": r["closes_at"],
            "open": bool(r["open"]),
            "yes_pool_points": r["s_yes_cents"] / 100.0,
            "no_pool_points":  r["s_no_cents"]  / 100.0,
            "odds": o,
            "implied_payout_per1": p,
        })
    return out

@router.get("/bets")
def list_bets_admin(
    x_admin_token: Optional[str] = Header(default=None, alias="X-Admin-Token"),
    limit: int = Query(default=100, ge=1, le=1000)
):
    _require_admin(x_admin_token)
    with conn() as c:
        rows = c.execute(
            """
            SELECT b.id, b.market_id, b.username, b.side, b.amount_cents, b.created_at,
                   m.question
            FROM bets b
            LEFT JOIN markets m ON m.id = b.market_id
            ORDER BY b.created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [
        {
            "id": r["id"],
            "market_id": r["market_id"],
            "question": r["question"],
            "username": r["username"],
            "side": r["side"],
            "amount_points": r["amount_cents"] / 100.0,
            "created_at": r["created_at"],
        }
        for r in rows
    ]

# --------- ACTIONS ---------

@router.post("/markets/{market_id}/close")
def close_market(market_id: str, x_admin_token: str = Header(default="", alias="X-Admin-Token")):
    _require_admin(x_admin_token)
    with conn() as c:
        cur = c.execute("UPDATE markets SET open=0 WHERE id=? AND open=1", (market_id,))
        if cur.rowcount == 0:
            raise HTTPException(404, "market not found or already closed")
    return {"ok": True}

@router.post("/markets/{market_id}/settle")
def settle_market(market_id: str, req: SettleReq, x_admin_token: str = Header(default="", alias="X-Admin-Token")):
    _require_admin(x_admin_token)
    winner = req.winner
    with conn() as c:
        m = c.execute(
            "SELECT s_yes_cents, s_no_cents, open FROM markets WHERE id=?",
            (market_id,)
        ).fetchone()
        if not m:
            raise HTTPException(404, "market not found")
        if bool(m["open"]):
            raise HTTPException(400, "close market before settlement")

        total = m["s_yes_cents"] + m["s_no_cents"]
        winner_pool = m["s_yes_cents"] if winner == "YES" else m["s_no_cents"]
        per1 = total / max(winner_pool, 1)

        rows = c.execute(
            "SELECT username, amount_cents FROM bets WHERE market_id=? AND side=?",
            (market_id, winner)
        ).fetchall()
        for r in rows:
            payout = int(round(r["amount_cents"] * per1))
            c.execute(
                "UPDATE users SET balance_cents = balance_cents + ? WHERE username=?",
                (payout, r["username"])
            )
    return {"ok": True, "winner": winner}

from fastapi import Header

@router.get("/debug/db")
def debug_db(x_admin_token: str = Header(default="", alias="X-Admin-Token")):
    _require_admin(x_admin_token)
    from ..db import DB_PATH
    import os, sqlite3
    exists = os.path.exists(DB_PATH)
    size = os.path.getsize(DB_PATH) if exists else 0
    with sqlite3.connect(DB_PATH) as con:
        con.row_factory = sqlite3.Row
        cur = con.execute("SELECT count(*) AS n FROM sqlite_master WHERE type='table'")
        tables = con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
    return {
        "db_path": DB_PATH,
        "exists": exists,
        "size": size,
        "table_count": cur.fetchone()["n"],
        "tables": [t["name"] for t in tables],
    }