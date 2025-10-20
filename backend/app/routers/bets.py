import uuid, datetime as dt
from fastapi import APIRouter, HTTPException
from ..db import conn
from ..logic import odds, implied_payout_per1
from ..schemas.bets import BetReq, BetResp

router = APIRouter()

@router.post("/markets/{market_id}/bet", response_model=BetResp)
def place_bet(market_id: str, req: BetReq):
    side = req.side.upper()
    if side not in ("YES", "NO"):
        raise HTTPException(400, "side must be YES or NO")
    add_cents = req.amount_points * 100
    now = dt.datetime.utcnow().isoformat()

    with conn() as c:
        m = c.execute("SELECT * FROM markets WHERE id=?", (market_id,)).fetchone()
        if not m: raise HTTPException(404, "market not found")
        if not bool(m["open"]): raise HTTPException(400, "market is closed")

        u = c.execute("SELECT balance_cents FROM users WHERE username=?", (req.username,)).fetchone()
        if not u: raise HTTPException(404, "user not found")
        if u["balance_cents"] < add_cents: raise HTTPException(400, "insufficient balance")

        # debit user
        c.execute("UPDATE users SET balance_cents = balance_cents - ? WHERE username=?", (add_cents, req.username))

        # upsert bet (additive policy)
        existing = c.execute(
            "SELECT id, amount_cents FROM bets WHERE market_id=? AND username=? AND side=?",
            (market_id, req.username, side)
        ).fetchone()
        if existing:
            c.execute("UPDATE bets SET amount_cents = amount_cents + ?, created_at=? WHERE id=?",
                      (add_cents, now, existing["id"]))
        else:
            c.execute("INSERT INTO bets (id, market_id, username, side, amount_cents, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                      (str(uuid.uuid4()), market_id, req.username, side, add_cents, now))

        # update pools
        if side == "YES":
            c.execute("UPDATE markets SET s_yes_cents = s_yes_cents + ? WHERE id=?", (add_cents, market_id))
        else:
            c.execute("UPDATE markets SET s_no_cents = s_no_cents + ? WHERE id=?", (add_cents, market_id))

        m2 = c.execute("SELECT s_yes_cents, s_no_cents FROM markets WHERE id=?", (market_id,)).fetchone()
        bal = c.execute("SELECT balance_cents FROM users WHERE username=?", (req.username,)).fetchone()

    s_yes, s_no = m2["s_yes_cents"], m2["s_no_cents"]
    return BetResp(
        ok=True,
        new_balance_points=bal["balance_cents"]/100.0,
        odds=odds(s_yes, s_no),
        implied_payout_per1=implied_payout_per1(s_yes, s_no)
    )

@router.get("/users/{username}/bets")
def user_bets(username: str):
    with conn() as c:
        rows = c.execute("""
          SELECT b.market_id, b.side, b.amount_cents, m.question, m.closes_at, m.open,
                 m.s_yes_cents, m.s_no_cents
          FROM bets b JOIN markets m ON m.id=b.market_id
          WHERE b.username=?
          ORDER BY b.created_at DESC
        """, (username,)).fetchall()
    out = []
    for r in rows:
        odds_ = odds(r["s_yes_cents"], r["s_no_cents"])
        pay_ = implied_payout_per1(r["s_yes_cents"], r["s_no_cents"])
        out.append({
            "market_id": r["market_id"],
            "question": r["question"],
            "closes_at": r["closes_at"],
            "open": bool(r["open"]),
            "side": r["side"],
            "amount_points": r["amount_cents"]/100.0,
            "odds": odds_,
            "implied_payout_per1": pay_
        })
    return out