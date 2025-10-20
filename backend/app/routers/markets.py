from fastapi import APIRouter, HTTPException, Header, Query
from typing import Optional
from ..db import conn
from ..schemas.markets import CreateMarketReq, MarketOut
from ..config import ADMIN_TOKEN
from ..logic import odds, implied_payout_per1

router = APIRouter()

@router.post("/markets", response_model=MarketOut)
def create_market(
    req: CreateMarketReq,
    x_admin_token: str | None = Header(default=None, alias="X-Admin-Token"),
):
    if x_admin_token != ADMIN_TOKEN:
        raise HTTPException(401, "Admin token required")

    yes_cents = int(round(req.seed_yes_points * 100))
    no_cents  = int(round(req.seed_no_points  * 100))
    if yes_cents == 0 and no_cents == 0:
        raise HTTPException(400, "At least one seed pool must be > 0")

    with conn() as c:
        c.execute(
            "INSERT INTO markets (id, question, closes_at, open, s_yes_cents, s_no_cents) "
            "VALUES (lower(hex(randomblob(8))), ?, ?, 1, ?, ?)",
            (req.question, req.closes_at.isoformat(), yes_cents, no_cents),
        )
        m = c.execute(
            "SELECT id, question, closes_at, open, s_yes_cents, s_no_cents "
            "FROM markets ORDER BY rowid DESC LIMIT 1"
        ).fetchone()

    return {
        "id": m["id"],
        "question": m["question"],
        "closes_at": m["closes_at"],
        "open": bool(m["open"]),
        "yes_pool_points": m["s_yes_cents"] / 100.0,
        "no_pool_points":  m["s_no_cents"]  / 100.0,
        "odds": odds(m["s_yes_cents"], m["s_no_cents"]),
        "implied_payout_per1": implied_payout_per1(m["s_yes_cents"], m["s_no_cents"]),
    }

@router.get("/markets", response_model=list[MarketOut])
def list_markets(status: Optional[str] = Query(default=None)):
    where = ""
    if status == "open":
        where = "WHERE open=1"
    elif status == "closed":
        where = "WHERE open=0"

    with conn() as c:
        rows = c.execute(
            f"SELECT id, question, closes_at, open, s_yes_cents, s_no_cents FROM markets {where} ORDER BY closes_at ASC"
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