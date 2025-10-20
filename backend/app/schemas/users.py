from pydantic import BaseModel, Field

class UserCreate(BaseModel):
    username: str
    starting_points: int = Field(1000, ge=0)

class UserOut(BaseModel):
    username: str
    balance_points: float