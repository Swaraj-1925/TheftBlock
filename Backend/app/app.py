from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine

from Backend.app.api import router

app = FastAPI(title="Inventory Management API")

# CORS setup for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5174"],  # React dev server and Vite
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Include API routes
app.include_router(router, prefix="/api")

