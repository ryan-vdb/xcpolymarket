# backend/app/routers/admin.py
# Admin utilities: list users/markets/bets, close/settle markets, (optional) delete markets.

from __future__ import annotations
from typing import Optional
from fastapi import APIRouter, HTTPException, Header, Query
from ..db import conn, DB_PATH
from ..config import ADMIN_TOKEN
from ..logic import effective_pools, odds_from_pools, implied_payout_per1_spot
from ..schemas.markets import SettleReq

router = APIRouter()

# --------- helpers ---------

def _require_admin(token: Optional[str]):
    if token != ADMIN_TOKEN:
        raise HTTPException(401, "admin token required")


# --------- LIST VIEWS ---------

@router.get("/users")
def list_users(
    x_admin_token: Optional[str] = Header(default=None, alias="X-Admin-Token")
):
    _require_admin(x_admin_token)
    with conn() as c:
        rows = c.execute(
            "SELECT username, balance_cents FROM users ORDER BY balance_cents DESC, username ASC"
        ).fetchall()
    return [
        {"username": r["username"], "balance_points": r["balance_cents"] / 100.0}
        for r in rows
    ]


@router.get("/markets")
def list_markets_admin(
    x_admin_token: Optional[str] = Header(default=None, alias="X-Admin-Token"),
    status: Optional[str] = Query(default=None)  # open | closed | settled | None
):
    _require_admin(x_admin_token)

    where = []
    if status == "open":
        where.append("open=1 AND settled=0")
    elif status == "closed":
        where.append("open=0 AND settled=0")
    elif status == "settled":
        where.append("settled=1")
    where_sql = f"WHERE {' AND '.join(where)}" if where else ""

    with conn() as c:
        rows = c.execute(
            f"""
            SELECT id, question, closes_at, open, settled, winner,
                   yes_real_cents, no_real_cents, virt_yes_cents, virt_no_cents
            FROM markets
            {where_sql}
            ORDER BY closes_at ASC
            """
        ).fetchall()

    out = []
    for r in rows:
        y_eff, n_eff = effective_pools(
            r["yes_real_cents"], r["no_real_cents"], r["virt_yes_cents"], r["virt_no_cents"]
        )
        out.append({
            "id": r["id"],
            "question": r["question"],
            "closes_at": r["closes_at"],
            "open": bool(r["open"]),
            "settled": bool(r["settled"]),
            "winner": r["winner"],
            "yes_pool_points": r["yes_real_cents"] / 100.0,
            "no_pool_points":  r["no_real_cents"]  / 100.0,
            "odds": odds_from_pools(y_eff, n_eff),
            "implied_payout_per1_spot": implied_payout_per1_spot(y_eff, n_eff),
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
            "spend_points": r["amount_cents"] / 100.0,
            "created_at": r["created_at"],
        }
        for r in rows
    ]


# --------- ACTIONS ---------

@router.post("/markets/{market_id}/close")
def close_market(
    market_id: str,
    x_admin_token: Optional[str] = Header(default=None, alias="X-Admin-Token"),
):
    _require_admin(x_admin_token)
    with conn() as c:
        cur = c.execute(
            "UPDATE markets SET open=0 WHERE id=? AND open=1 AND settled=0",
            (market_id,),
        )
        if cur.rowcount == 0:
            raise HTTPException(404, "market not found, already closed, or already settled")
    return {"ok": True}


@router.post("/markets/{market_id}/settle")
def settle_market(
    market_id: str,
    req: SettleReq,
    x_admin_token: str = Header(default="", alias="X-Admin-Token"),
):
    _require_admin(x_admin_token)
    winner = req.winner  # "YES" or "NO"

    with conn() as c:
        # Load market (must be closed & not yet settled)
        m = c.execute(
            """
            SELECT open, settled,
                   yes_real_cents, no_real_cents
            FROM markets WHERE id=?
            """,
            (market_id,),
        ).fetchone()

        if not m:
            raise HTTPException(404, "market not found")
        if bool(m["open"]):
            raise HTTPException(400, "close market before settlement")
        if bool(m["settled"]):
            return {"ok": True, "winner": winner, "total_paid_points": 0.0}

        # Determine winner-side shares column
        if winner == "YES":
            shares_col = "yes_shares_points"
            pool_cents = m["yes_real_cents"]
        else:
            shares_col = "no_shares_points"
            pool_cents = m["no_real_cents"]

        # Sum total winner shares (in *points*, float)
        row = c.execute(
            f"SELECT COALESCE(SUM({shares_col}), 0.0) AS total_shares FROM positions WHERE market_id=?",
            (market_id,),
        ).fetchone()
        total_winner_shares_points = row["total_shares"] or 0.0

        total_paid_cents = 0

        if total_winner_shares_points > 0 and pool_cents > 0:
            # Pay each holder pro-rata from the real pool (points = dollars)
            holders = c.execute(
                f"""
                SELECT username, {shares_col} AS sh
                FROM positions
                WHERE market_id=? AND {shares_col} > 0
                """,
                (market_id,),
            ).fetchall()

            for h in holders:
                ratio = float(h["sh"]) / float(total_winner_shares_points)
                pay_cents = int(round(pool_cents * ratio))
                if pay_cents > 0:
                    c.execute(
                        "UPDATE users SET balance_cents = balance_cents + ? WHERE username=?",
                        (pay_cents, h["username"]),
                    )
                    total_paid_cents += pay_cents

        # Mark market settled
        c.execute(
            "UPDATE markets SET settled=1, winner=? WHERE id=?",
            (winner, market_id),
        )

    return {"ok": True, "winner": winner, "total_paid_points": total_paid_cents / 100.0}


@router.delete("/markets/{market_id}")
def delete_market(
    market_id: str,
    x_admin_token: Optional[str] = Header(default=None, alias="X-Admin-Token"),
    force: bool = Query(default=False, description="Allow deleting even if settled (dev only)"),
):
    """
    Hard-delete a market and related rows. For development/testing only.
    By default, refuses to delete if already settled.
    """
    _require_admin(x_admin_token)
    with conn() as c:
        m = c.execute(
            "SELECT id, settled FROM markets WHERE id=?",
            (market_id,),
        ).fetchone()
        if not m:
            raise HTTPException(404, "market not found")
        if bool(m["settled"]) and not force:
            raise HTTPException(400, "market already settled; pass force=true to delete anyway (dev only)")

        try:
            c.execute("BEGIN")
            c.execute("DELETE FROM bets WHERE market_id=?", (market_id,))
            c.execute("DELETE FROM positions WHERE market_id=?", (market_id,))
            c.execute("DELETE FROM markets WHERE id=?", (market_id,))
            c.execute("COMMIT")
        except Exception as e:
            c.execute("ROLLBACK")
            raise HTTPException(500, f"delete failed: {e}")

    return {"ok": True}


# --------- DEBUG ---------

@router.get("/debug/db")
def debug_db(x_admin_token: Optional[str] = Header(default=None, alias="X-Admin-Token")):
    _require_admin(x_admin_token)
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