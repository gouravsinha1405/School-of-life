from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, journal, report, user
from app.core.config import settings
from app.core.logging import configure_logging

configure_logging()

app = FastAPI(title="Lebensschule API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(journal.router)
app.include_router(report.router)
app.include_router(user.router)


@app.get("/")
def root():
    return {"message": "Lebensschule API"}
