# backend/app/schemas/markets.py
from __future__ import annotations
from typing import Dict, Literal, Optional
from pydantic import BaseModel, Field
from datetime import datetime

Winner = Literal["YES", "NO"]

class CreateMarketReq(BaseModel):
    """
    Admin-only create payload. Virtual depth is expressed in *points*.
    """
    question: str = Field(min_length=5, max_length=200)
    # You can accept either ISO string or datetime; FastAPI will coerce from ISO.
    closes_at: datetime
    seed_yes_points: float = Field(5, ge=0)  # defaults are safe for dev
    seed_no_points: float  = Field(5, ge=0)

class MarketOut(BaseModel):
    """
    Shape returned by GET /markets and GET /markets/{id}.
    Mirrors what routers/markets.py assembles from effective pools.
    """
    id: str
    question: str
    # Stored as TEXT in SQLite; we return it serialized as ISO string.
    closes_at: str
    open: bool
    settled: bool
    winner: Optional[Winner] = None

    # Debug/transparent: real money that has flowed into each side (in points)
    yes_pool_points: float
    no_pool_points: float

    # Pricing (derived from effective = real + virtual)
    odds: Dict[str, float]                # {"yes": p_yes, "no": p_no}
    price_yes: float                      # spot price of YES (0..1)
    implied_payout_per1_spot: Dict[str, float]  # {"yes": 1/p_yes, "no": 1/p_no}

class SettleReq(BaseModel):
    winner: Winner