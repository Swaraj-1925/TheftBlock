from typing import Union

from app.inventory_routes import inventory_router
from app.supplier_routes import supplier_router
from app.testing_routes import test_router
from src.Db.db import get_session, async_engine, create_db_and_tables
from sqlmodel import SQLModel

from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()  # Initialize DB
    yield  # The app runs here
    print("Shutting down...")

app = FastAPI(lifespan=lifespan)
app.include_router(router=inventory_router)
app.include_router(router=supplier_router)
app.include_router(router=test_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Change this for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
async def root():
    return {"message": "Hello World"}

