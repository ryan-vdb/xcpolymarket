from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import users, markets, bets, admin, auth

app = FastAPI(title="Prediction Market (Pari-mutuel)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"ok": True}

app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(markets.router, prefix="/markets", tags=["markets"])
app.include_router(bets.router, tags=["bets"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])