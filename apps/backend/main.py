"""
DdangHa Backend API
FastAPI application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="DdangHa API",
    description="Launchpad Backend API",
    version="0.1.0",
)

# CORS 설정 (로컬 개발용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
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
