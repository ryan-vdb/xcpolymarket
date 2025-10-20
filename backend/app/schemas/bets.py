from pydantic import BaseModel, Field, validator
from typing import Dict

class BetReq(BaseModel):
    # Username comes from JWT; do NOT include it in requests
    side: str = Field(pattern="^(YES|NO)$")
    amount_points: float = Field(..., gt=0, le=1_000_000)

    @validator("amount_points")
    def two_decimals(cls, v: float):
        # enforce up to 2 decimals
        if round(v, 2) != v:
            raise ValueError("amount_points must have at most 2 decimals")
        return v

class BetResp(BaseModel):
    ok: bool
    new_balance_points: float
    odds: Dict[str, float]
    implied_payout_per1: Dict[str, float]