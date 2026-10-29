
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router

api = FastAPI(
    title="UK Wind Generation Forecast Accuracy API",
    version="1.0.0",
)

@api.get("/")
def home():
    return {"message": "GridBricks API is running"}

@api.get("/health")
def health():
    return {"status": "healthy"}

api.include_router(router)

cors_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "https://gridbricks-ele-gen-2.onrender.com,http://localhost:5173,http://localhost:4173",
    ).split(",")
    if origin.strip()
]

# Wrap the entire FastAPI application with CORS middleware
app = CORSMiddleware(
    app=api,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
