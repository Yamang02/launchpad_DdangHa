"""
DdangHa Backend API
FastAPI application entry point
"""
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

_ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS")
if not _ALLOWED_ORIGINS:
    raise ValueError("ALLOWED_ORIGINS environment variable is required")

app = FastAPI(
    title="DdangHa API",
    description="Launchpad Backend API",
    version="0.1.0",
)

# CORS 설정 (ALLOWED_ORIGINS env 필수)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _ALLOWED_ORIGINS.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "DdangHa API is running", "status": "ok"}


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}
