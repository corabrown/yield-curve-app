from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import users, yield_curve

app = FastAPI(
    title="Yield Curve API",
    description="Serves US Treasury yield curve data.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten when frontend origin is known
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(yield_curve.router)
app.include_router(users.router)


@app.get("/health")
def health():
    return {"status": "ok"}
