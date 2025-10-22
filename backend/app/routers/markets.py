# backend/app/routers/markets.py
# Market listing & creation using CPMM pools (real + virtual).

from __future__ import annotations
import uuid
from fastapi import APIRouter, HTTPException, Header, Query
from typing import Optional, List
from ..db import conn
from ..config import ADMIN_TOKEN
from ..schemas.markets import CreateMarketReq
from ..logic import effective_pools, odds_from_pools, implied_payout_per1_spot, spot_price_yes

router = APIRouter()


# --------- helpers ---------

def _rows_to_market_out(rows) -> List[dict]:
    out = []
    for r in rows:
        yes_eff, no_eff = effective_pools(
            r["yes_real_cents"],
            r["no_real_cents"],
            r["virt_yes_cents"],
            r["virt_no_cents"],
        )
        out.append({
            "id": r["id"],
            "question": r["question"],
            "closes_at": r["closes_at"],
            "open": bool(r["open"]),
            "settled": bool(r["settled"]),
            "winner": r["winner"],
            # real pools in points (for transparency/debug)
            "yes_pool_points": r["yes_real_cents"] / 100.0,
            "no_pool_points":  r["no_real_cents"]  / 100.0,
            # pricing (effective pools drive these)
            "odds": odds_from_pools(yes_eff, no_eff),
            "price_yes": spot_price_yes(yes_eff, no_eff),
            "implied_payout_per1_spot": implied_payout_per1_spot(yes_eff, no_eff),
        })
    return out


# --------- list / read ---------

@router.get("/markets")
def list_markets(
    status: Optional[str] = Query(default=None, description="open | closed | settled"),
):
    """
    List markets. `status` can be:
      - open:    open=1 and settled=0
      - closed:  open=0 and settled=0
      - settled: settled=1
      - None:    all
    """
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
    return _rows_to_market_out(rows)


@router.get("/markets/{market_id}")
def get_market(market_id: str):
    with conn() as c:
        r = c.execute(
            """
            SELECT id, question, closes_at, open, settled, winner,
                   yes_real_cents, no_real_cents, virt_yes_cents, virt_no_cents
            FROM markets WHERE id=?
            """,
            (market_id,),
        ).fetchone()
        if not r:
            raise HTTPException(404, "market not found")
    return _rows_to_market_out([r])[0]


# --------- create (admin) ---------

@router.post("/markets")
def create_market(req: CreateMarketReq, x_admin_token: str = Header(default="")):
    """
    Create a market with virtual depth. Only admins (X-Admin-Token) can create.

    Body:
      {
        "question": "Will X happen?",
        "closes_at": "2026-01-01T00:00:00Z",
        "seed_yes_points": 1000,
        "seed_no_points":  1000
      }
    """
    if x_admin_token != ADMIN_TOKEN:
        raise HTTPException(401, "admin token required")

    if req.seed_yes_points < 0 or req.seed_no_points < 0:
        raise HTTPException(400, "seed points must be >= 0")

    m_id = str(uuid.uuid4())
    virt_yes_cents = int(round(req.seed_yes_points * 100))
    virt_no_cents  = int(round(req.seed_no_points  * 100))

    with conn() as c:
        try:
            c.execute(
                """
                INSERT INTO markets
                  (id, question, closes_at, open, settled, winner,
                   yes_real_cents, no_real_cents, virt_yes_cents, virt_no_cents)
                VALUES
                  (?,  ?,        ?,         1,    0,       NULL,
                   0,              0,             ?,              ?)
                """,
                (m_id, req.question, req.closes_at, virt_yes_cents, virt_no_cents),
            )
        except Exception as e:
            raise HTTPException(400, f"create failed: {e}")

        r = c.execute(
            """
            SELECT id, question, closes_at, open, settled, winner,
                   yes_real_cents, no_real_cents, virt_yes_cents, virt_no_cents
            FROM markets WHERE id=?
            """,
            (m_id,),
        ).fetchone()

    return _rows_to_market_out([r])[0]