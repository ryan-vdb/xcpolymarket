from fastapi import FastAPI
from .routers import users, markets, bets, admin

app = FastAPI(title="Prediction Market (Pari-mutuel)")

@app.get("/health")
def health():
    return {"ok": True}

app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(markets.router, prefix="/markets", tags=["markets"])
app.include_router(bets.router, tags=["bets"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])