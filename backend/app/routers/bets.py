# backend/app/routers/bets.py
import uuid, datetime as dt
from typing import Literal
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from ..db import conn
from ..auth import get_current_username
from ..logic import cpmm_buy_yes, cpmm_buy_no, cpmm_price_yes

router = APIRouter()

# Request/Response models specific to trading via AMM
class TradeReq(BaseModel):
    side: Literal["YES", "NO"]
    amount_points: int = Field(..., gt=0, description="How many points to spend (1 point = 1$ in your system)")

class TradeResp(BaseModel):
    ok: bool
    filled_shares: float          # number of shares received (each share settles to 1 point-dollar if winner)
    new_price_yes: float          # post-trade quoted price of YES (0..1)
    new_balance_points: float     # user's new balance (points)

@router.post("/markets/{market_id}/trade", response_model=TradeResp)
def trade(market_id: str, req: TradeReq, username: str = Depends(get_current_username)):
    """
    Buy YES/NO shares from the CPMM.
    - Debits user's balance by `amount_points`.
    - Updates market pools.
    - Credits user's YES or NO shares in `positions`.
    """
    cash_cents = int(round(req.amount_points * 100))
    if cash_cents <= 0:
        raise HTTPException(400, "amount_points must be > 0")

    now = dt.datetime.utcnow().isoformat()

    with conn() as c:
        try:
            c.execute("BEGIN")

            m = c.execute(
                "SELECT open, s_yes_cents AS py, s_no_cents AS pn FROM markets WHERE id=?",
                (market_id,)
            ).fetchone()
            if not m:
                raise HTTPException(404, "market not found")
            if not bool(m["open"]):
                raise HTTPException(400, "market closed")

            u = c.execute(
                "SELECT balance_cents FROM users WHERE username=?",
                (username,)
            ).fetchone()
            if not u:
                raise HTTPException(404, "user not found")
            if u["balance_cents"] < cash_cents:
                raise HTTPException(400, "insufficient balance")

            py, pn = int(m["py"]), int(m["pn"])

            if req.side == "YES":
                shares, new_py, new_pn = cpmm_buy_yes(py, pn, cash_cents)
                if shares <= 0:
                    raise HTTPException(400, "trade too small")
                # update pools
                c.execute("UPDATE markets SET s_yes_cents=?, s_no_cents=? WHERE id=?", (new_py, new_pn, market_id))
                # upsert position
                row = c.execute(
                    "SELECT id FROM positions WHERE market_id=? AND username=?",
                    (market_id, username)
                ).fetchone()
                if row:
                    c.execute(
                        "UPDATE positions SET yes_shares_cents = yes_shares_cents + ?, created_at=? WHERE id=?",
                        (shares, now, row["id"])
                    )
                else:
                    c.execute(
                        "INSERT INTO positions (id, market_id, username, yes_shares_cents, no_shares_cents, created_at) "
                        "VALUES (?, ?, ?, ?, ?, ?)",
                        (str(uuid.uuid4()), market_id, username, shares, 0, now)
                    )
                price_yes = cpmm_price_yes(new_py, new_pn)
            else:
                shares, new_py, new_pn = cpmm_buy_no(py, pn, cash_cents)
                if shares <= 0:
                    raise HTTPException(400, "trade too small")
                c.execute("UPDATE markets SET s_yes_cents=?, s_no_cents=? WHERE id=?", (new_py, new_pn, market_id))
                row = c.execute(
                    "SELECT id FROM positions WHERE market_id=? AND username=?",
                    (market_id, username)
                ).fetchone()
                if row:
                    c.execute(
                        "UPDATE positions SET no_shares_cents = no_shares_cents + ?, created_at=? WHERE id=?",
                        (shares, now, row["id"])
                    )
                else:
                    c.execute(
                        "INSERT INTO positions (id, market_id, username, yes_shares_cents, no_shares_cents, created_at) "
                        "VALUES (?, ?, ?, ?, ?, ?)",
                        (str(uuid.uuid4()), market_id, username, 0, shares, now)
                    )
                price_yes = cpmm_price_yes(new_py, new_pn)

            # debit user
            c.execute("UPDATE users SET balance_cents = balance_cents - ? WHERE username=?", (cash_cents, username))
            new_bal = c.execute(
                "SELECT balance_cents FROM users WHERE username=?",
                (username,)
            ).fetchone()["balance_cents"]

            c.execute("COMMIT")
        except HTTPException:
            c.execute("ROLLBACK")
            raise
        except Exception as e:
            c.execute("ROLLBACK")
            raise HTTPException(500, f"Trade failed: {e}")

    return TradeResp(
        ok=True,
        filled_shares=shares / 100.0,
        new_price_yes=price_yes,
        new_balance_points=new_bal / 100.0
    )