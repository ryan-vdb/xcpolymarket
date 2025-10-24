# backend/app/routers/bets.py
# Place a trade into the CPMM, debit user balance, mint shares, and move price.

from __future__ import annotations
import uuid, datetime as dt
from fastapi import APIRouter, HTTPException, Depends
from ..db import conn
from ..auth import get_current_username
from ..schemas.bets import BetReq, BetResp
from ..logic import apply_buy, effective_pools, odds_from_pools, implied_payout_per1_spot

router = APIRouter()

@router.post("/markets/{market_id}/bet", response_model=BetResp)
def place_bet(
    market_id: str,
    req: BetReq,
    username: str = Depends(get_current_username),
):
    # normalize/validate
    side = req.side.upper().strip()
    if side not in ("YES", "NO"):
        raise HTTPException(400, "side must be YES or NO")

    spend_cents = int(round(req.spend_points * 100))
    if spend_cents <= 0:
        raise HTTPException(400, "spend_points must be > 0")

    now = dt.datetime.utcnow().isoformat()

    with conn() as c:
        try:
            c.execute("BEGIN")

            # Market must exist and be open
            m = c.execute(
                """
                SELECT id, open, closes_at,
                       yes_real_cents, no_real_cents,
                       virt_yes_cents, virt_no_cents
                FROM markets
                WHERE id=?
                """,
                (market_id,),
            ).fetchone()
            if not m:
                raise HTTPException(404, "market not found")
            if not bool(m["open"]):
                raise HTTPException(400, "market is closed")

            # User must exist & have balance
            u = c.execute(
                "SELECT balance_cents FROM users WHERE username=?",
                (username,),
            ).fetchone()
            if not u:
                raise HTTPException(404, "user not found")
            if u["balance_cents"] < spend_cents:
                raise HTTPException(400, "insufficient balance")

            # Compute CPMM outcome (pure math, no side-effects)
            out = apply_buy(
                side=side,
                spend_cents=spend_cents,
                yes_real_cents=m["yes_real_cents"],
                no_real_cents=m["no_real_cents"],
                virt_yes_cents=m["virt_yes_cents"],
                virt_no_cents=m["virt_no_cents"],
            )

            # 1) Debit user
            c.execute(
                "UPDATE users SET balance_cents = balance_cents - ? WHERE username=?",
                (spend_cents, username),
            )

            # 2) Update market real pools
            c.execute(
                """
                UPDATE markets
                   SET yes_real_cents=?, no_real_cents=?
                 WHERE id=?
                """,
                (out["new_yes_real_cents"], out["new_no_real_cents"], market_id),
            )

            # 3) Upsert positions (store issued shares in points as REAL)
            add_yes_points = out["shares_points_issued"] if side == "YES" else 0.0
            add_no_points  = out["shares_points_issued"] if side == "NO"  else 0.0

            pos = c.execute(
                "SELECT yes_shares_points, no_shares_points FROM positions WHERE market_id=? AND username=?",
                (market_id, username),
            ).fetchone()

            if pos:
                c.execute(
                    """
                    UPDATE positions
                       SET yes_shares_points = yes_shares_points + ?,
                           no_shares_points  = no_shares_points  + ?,
                           created_at = ?
                     WHERE market_id=? AND username=?
                    """,
                    (add_yes_points, add_no_points, now, market_id, username),
                )
            else:
                c.execute(
                    """
                    INSERT INTO positions (id, market_id, username, yes_shares_points, no_shares_points, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (str(uuid.uuid4()), market_id, username, add_yes_points, add_no_points, now),
                )

            # 4) Append to bets ledger (optional but useful)
            c.execute(
                """
                INSERT INTO bets (id, market_id, username, side, amount_cents, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (str(uuid.uuid4()), market_id, username, side, spend_cents, now),
            )

            # New balance for response
            new_bal = c.execute(
                "SELECT balance_cents FROM users WHERE username=?",
                (username,),
            ).fetchone()["balance_cents"]

            c.execute("COMMIT")

        except HTTPException:
            c.execute("ROLLBACK")
            raise
        except Exception as e:
            c.execute("ROLLBACK")
            raise HTTPException(500, f"Bet failed: {e}")

    # Response odds/price from effective pools AFTER trade
    yes_eff, no_eff = effective_pools(
        out["new_yes_real_cents"], out["new_no_real_cents"],
        m["virt_yes_cents"], m["virt_no_cents"]
    )
    odds_after = odds_from_pools(yes_eff, no_eff)
    implied = implied_payout_per1_spot(yes_eff, no_eff)

    return BetResp(
        ok=True,
        new_balance_points=new_bal / 100.0,
        shares_points_issued=out["shares_points_issued"],
        price_yes_after=out["price_yes_after"],
        odds=odds_after,
        implied_payout_per1_spot=implied,
    )