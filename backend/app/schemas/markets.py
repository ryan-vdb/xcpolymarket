from pydantic import BaseModel, Field
from typing import Literal, Optional, Dict

class MarketCreate(BaseModel):
    question: str
    closes_at: str         # ISO string (UTC recommended)
    seed_yes_points: int = Field(100, ge=0)
    seed_no_points: int = Field(100, ge=0)

class MarketOut(BaseModel):
    id: str
    question: str
    closes_at: str
    open: bool
    s_yes_cents: int
    s_no_cents: int
    odds: Dict[str, float]
    implied_payout_per1: Dict[str, float]

class SettleReq(BaseModel):
    winner: Literal["YES", "NO"]