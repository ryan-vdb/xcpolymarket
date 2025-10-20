from fastapi import APIRouter, HTTPException, Header
from ..db import conn
from ..config import ADMIN_TOKEN
from ..schemas.markets import SettleReq

router = APIRouter()

def _require_admin(token: str):
    if token != ADMIN_TOKEN:
        raise HTTPException(401, "admin token required")

@router.post("/markets/{market_id}/close")
def close_market(market_id: str, x_admin_token: str = Header(default="")):
    _require_admin(x_admin_token)
    with conn() as c:
        cur = c.execute("UPDATE markets SET open=0 WHERE id=? AND open=1", (market_id,))
        if cur.rowcount == 0:
            raise HTTPException(404, "market not found or already closed")
    return {"ok": True}

@router.post("/markets/{market_id}/settle")
def settle_market(market_id: str, req: SettleReq, x_admin_token: str = Header(default="")):
    _require_admin(x_admin_token)
    winner = req.winner
    with conn() as c:
        m = c.execute("SELECT s_yes_cents, s_no_cents, open FROM markets WHERE id=?", (market_id,)).fetchone()
        if not m: raise HTTPException(404, "market not found")
        if bool(m["open"]): raise HTTPException(400, "close market before settlement")

        total = m["s_yes_cents"] + m["s_no_cents"]
        winner_pool = m["s_yes_cents"] if winner == "YES" else m["s_no_cents"]
        per1 = total / max(winner_pool, 1)

        rows = c.execute("SELECT username, amount_cents FROM bets WHERE market_id=? AND side=?",
                         (market_id, winner)).fetchall()
        for r in rows:
            payout = int(round(r["amount_cents"] * per1))
            c.execute("UPDATE users SET balance_cents = balance_cents + ? WHERE username=?",
                      (payout, r["username"]))
    return {"ok": True, "winner": winner}