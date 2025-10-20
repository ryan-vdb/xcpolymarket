from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .routers import users, markets, bets, auth, admin

app = FastAPI(title="Prediction Market API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers (note the /users prefix)
app.include_router(auth.router,    prefix="/auth",  tags=["auth"])
app.include_router(users.router,   prefix="/users", tags=["users"])
app.include_router(markets.router, prefix="",       tags=["markets"])
app.include_router(bets.router,    prefix="",       tags=["bets"])
app.include_router(admin.router,   prefix="/admin", tags=["admin"])

@app.get("/health")
def health():
    return {"ok": True}

@app.exception_handler(HTTPException)
async def http_exc_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": str(exc.detail)})

@app.exception_handler(Exception)
async def unhandled_exc_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"error": "Internal server error"})