from pydantic import BaseModel, Field
from typing import Dict, Literal
from datetime import datetime

class CreateMarketReq(BaseModel):
    question: str = Field(min_length=5, max_length=160)
    closes_at: datetime
    seed_yes_points: float = Field(ge=0, le=1_000_000)
    seed_no_points: float = Field(ge=0, le=1_000_000)

class MarketOut(BaseModel):
    id: str
    question: str
    closes_at: datetime
    open: bool
    yes_pool_points: float
    no_pool_points: float
    odds: Dict[str, float]
    implied_payout_per1: Dict[str, float]

class SettleReq(BaseModel):
    winner: Literal["YES", "NO"]