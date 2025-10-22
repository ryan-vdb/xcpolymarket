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
    """Execute a CPMM buy (YES or NO) spending `spend_points` from the user's balance.

    - Converts spend_points → cents.
    - Ensures market exists and is open.
    - Ensures user has sufficient balance.
    - Uses logic.apply_buy(...) to calculate shares and new pools.
    - Updates markets.{yes_real_cents,no_real_cents}.
    - UPSERT into positions (yes_shares_points/no_shares_points).
    - Optionally logs a row in bets (ledger).
    - Returns new balance and post-trade odds/price.
    """
    # convert points -> cents (ints)
    spend_cents = int(round(req.spend_points * 100))
    if spend_cents <= 0:
        raise HTTPException(400, "spend_points must be > 0")

    now = dt.datetime.utcnow().isoformat()

    with conn() as c:
        try:
            c.execute("BEGIN")

            # --- Load market and ensure tradable
            m = c.execute(
                """
                SELECT id, open, closes_at,
                       yes_real_cents, no_real_cents,
                       virt_yes_cents, virt_no_cents
                FROM markets WHERE id=?
                """,
                (market_id,),
            ).fetchone()
            if not m:
                raise HTTPException(404, "market not found")
            if not bool(m["open"]):
                raise HTTPException(400, "market is closed")

            # --- Load user & check balance
            u = c.execute(
                "SELECT balance_cents FROM users WHERE username=?",
                (username,),
            ).fetchone()
            if not u:
                raise HTTPException(404, "user not found")
            if u["balance_cents"] < spend_cents:
                raise HTTPException(400, "insufficient balance")

            # --- Compute CPMM outcome (does not mutate DB)
            out = apply_buy(
                side=req.side,
                spend_cents=spend_cents,
                yes_real_cents=m["yes_real_cents"],
                no_real_cents=m["no_real_cents"],
                virt_yes_cents=m["virt_yes_cents"],
                virt_no_cents=m["virt_no_cents"],
            )

            # --- Persist: debit user, update pools, upsert positions, append ledger
            c.execute(
                "UPDATE users SET balance_cents = balance_cents - ? WHERE username=?",
                (spend_cents, username),
            )

            c.execute(
                """
                UPDATE markets
                   SET yes_real_cents=?, no_real_cents=?
                 WHERE id=?
                """,
                (out["new_yes_real_cents"], out["new_no_real_cents"], market_id),
            )

            # positions: one row per (market_id, username)
            pos = c.execute(
                "SELECT yes_shares_points, no_shares_points FROM positions WHERE market_id=? AND username=?",
                (market_id, username),
            ).fetchone()

            if req.side == "YES":
                add_yes = out["shares_points_issued"]
                add_no = 0.0
            else:
                add_yes = 0.0
                add_no = out["shares_points_issued"]

            if pos:
                c.execute(
                    """
                    UPDATE positions
                       SET yes_shares_points = yes_shares_points + ?,
                           no_shares_points  = no_shares_points  + ?
                     WHERE market_id=? AND username=?
                    """,
                    (add_yes, add_no, market_id, username),
                )
            else:
                c.execute(
                    """
                    INSERT INTO positions (market_id, username, yes_shares_points, no_shares_points, created_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (market_id, username, add_yes, add_no, now),
                )

            # optional: append to bets ledger for audit/history
            c.execute(
                """
                INSERT INTO bets (id, market_id, username, side, amount_cents, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (str(uuid.uuid4()), market_id, username, req.side, spend_cents, now),
            )

            # fetch new user balance for response
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

    # Also compute odds/implied from *current effective* pools for the response
    yes_eff, no_eff = effective_pools(
        out["new_yes_real_cents"], out["new_no_real_cents"], m["virt_yes_cents"], m["virt_no_cents"]
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