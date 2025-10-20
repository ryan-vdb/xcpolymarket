import uuid, datetime as dt
from fastapi import APIRouter, HTTPException, Query
from ..db import conn
from ..logic import odds, implied_payout_per1
from ..schemas.markets import MarketCreate, MarketOut

router = APIRouter()

def _row_to_market_out(row) -> MarketOut:
    s_yes = row["s_yes_cents"]; s_no = row["s_no_cents"]
    return MarketOut(
        id=row["id"],
        question=row["question"],
        closes_at=row["closes_at"],
        open=bool(row["open"]),
        s_yes_cents=s_yes,
        s_no_cents=s_no,
        odds=odds(s_yes, s_no),
        implied_payout_per1=implied_payout_per1(s_yes, s_no)
    )

@router.post("", response_model=MarketOut)
def create_market(req: MarketCreate):
    mid = str(uuid.uuid4())
    # store cents
    s_yes_c = req.seed_yes_points * 100
    s_no_c = req.seed_no_points * 100
    # basic ISO sanity check
    try:
        dt.datetime.fromisoformat(req.closes_at.replace("Z",""))
    except Exception:
        raise HTTPException(400, "closes_at must be ISO datetime string")
    with conn() as c:
        c.execute("""
            INSERT INTO markets(id, question, closes_at, open, s_yes_cents, s_no_cents)
            VALUES (?, ?, ?, 1, ?, ?)
        """, (mid, req.question, req.closes_at, s_yes_c, s_no_c))
        row = c.execute("SELECT * FROM markets WHERE id=?", (mid,)).fetchone()
    return _row_to_market_out(row)

@router.get("", response_model=list[MarketOut])
def list_markets(status: str = Query("open")):
    where = "open=1" if status == "open" else "1=1"
    with conn() as c:
        rows = c.execute(f"SELECT * FROM markets WHERE {where} ORDER BY closes_at ASC").fetchall()
    return [_row_to_market_out(r) for r in rows]

@router.get("/{market_id}", response_model=MarketOut)
def get_market(market_id: str):
    with conn() as c:
        row = c.execute("SELECT * FROM markets WHERE id=?", (market_id,)).fetchone()
        if not row:
            raise HTTPException(404, "market not found")
    return _row_to_market_out(row)