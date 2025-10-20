import uuid, datetime as dt
from fastapi import APIRouter, HTTPException, Depends
from ..db import conn
from ..logic import odds, implied_payout_per1
from ..schemas.bets import BetReq, BetResp
from ..auth import get_current_username  # JWT -> username

router = APIRouter()

@router.post("/markets/{market_id}/bet", response_model=BetResp)
def place_bet(
    market_id: str,
    req: BetReq,
    username: str = Depends(get_current_username),
):
    side = req.side.upper()
    if side not in ("YES", "NO"):
        raise HTTPException(400, "side must be YES or NO")

    add_cents = int(round(req.amount_points * 100))
    if add_cents <= 0:
        raise HTTPException(400, "amount must be > 0")

    now = dt.datetime.utcnow().isoformat()

    with conn() as c:
        try:
            c.execute("BEGIN")

            m = c.execute("SELECT * FROM markets WHERE id=?", (market_id,)).fetchone()
            if not m:
                raise HTTPException(404, "market not found")
            if not bool(m["open"]):
                raise HTTPException(400, "market is closed")

            u = c.execute("SELECT balance_cents FROM users WHERE username=?", (username,)).fetchone()
            if not u:
                raise HTTPException(404, "user not found")
            if u["balance_cents"] < add_cents:
                raise HTTPException(400, "insufficient balance")

            # debit user
            c.execute(
                "UPDATE users SET balance_cents = balance_cents - ? WHERE username=?",
                (add_cents, username),
            )

            # upsert bet
            ex = c.execute(
                "SELECT id, amount_cents FROM bets WHERE market_id=? AND username=? AND side=?",
                (market_id, username, side),
            ).fetchone()

            if ex:
                c.execute(
                    "UPDATE bets SET amount_cents = amount_cents + ?, created_at=? WHERE id=?",
                    (add_cents, now, ex["id"]),
                )
            else:
                c.execute(
                    "INSERT INTO bets (id, market_id, username, side, amount_cents, created_at) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (str(uuid.uuid4()), market_id, username, side, add_cents, now),
                )

            # update pools (rename if your columns differ)
            if side == "YES":
                c.execute("UPDATE markets SET s_yes_cents = s_yes_cents + ? WHERE id=?", (add_cents, market_id))
            else:
                c.execute("UPDATE markets SET s_no_cents  = s_no_cents  + ? WHERE id=?", (add_cents, market_id))

            m2  = c.execute("SELECT s_yes_cents, s_no_cents FROM markets WHERE id=?", (market_id,)).fetchone()
            bal = c.execute("SELECT balance_cents FROM users WHERE username=?", (username,)).fetchone()

            c.execute("COMMIT")
        except HTTPException:
            c.execute("ROLLBACK")
            raise
        except Exception as e:
            c.execute("ROLLBACK")
            raise HTTPException(500, f"Bet failed: {e}")

    s_yes, s_no = m2["s_yes_cents"], m2["s_no_cents"]
    return BetResp(
        ok=True,
        new_balance_points=bal["balance_cents"] / 100.0,
        odds=odds(s_yes, s_no),
        implied_payout_per1=implied_payout_per1(s_yes, s_no),
    )