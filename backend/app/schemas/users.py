from pydantic import BaseModel, Field

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=32)
    starting_points: int = Field(50, ge=0)

class UserOut(BaseModel):
    username: str
    balance_points: float
    # optional: include created_at later if you have it in DB