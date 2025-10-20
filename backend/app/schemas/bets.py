from pydantic import BaseModel, Field
from typing import Dict

class BetReq(BaseModel):
    username: str
    side: str  # "YES" | "NO"
    amount_points: int = Field(..., gt=0)

class BetResp(BaseModel):
    ok: bool
    new_balance_points: float
    odds: Dict[str, float]
    implied_payout_per1: Dict[str, float]