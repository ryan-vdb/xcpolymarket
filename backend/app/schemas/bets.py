# backend/app/schemas/bets.py
from pydantic import BaseModel, Field
from typing import Dict, Literal

Side = Literal["YES", "NO"]

class BetReq(BaseModel):
    side: Side
    # Amount the user wants to SPEND from balance (in points; 1 point = 100 cents).
    spend_points: float = Field(..., gt=0)

class BetResp(BaseModel):
    ok: bool
    new_balance_points: float
    # Shares issued to the user by this trade (points of $1 payout each)
    shares_points_issued: float
    # Spot price of YES after the fill (0..1)
    price_yes_after: float
    # Current odds after the fill (from effective pools)
    odds: Dict[str, float]
    # UI helper: 1/price spot multiples (not average fill)
    implied_payout_per1_spot: Dict[str, float]