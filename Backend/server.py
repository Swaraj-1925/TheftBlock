from typing import Union

from Backend.app.inventory_routes import inventory_router
from Backend.src.Db.db import get_session, async_engine, create_db_and_tables
from sqlmodel import SQLModel

from fastapi import FastAPI
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()  # Initialize DB
    yield  # The app runs here
    print("Shutting down...")

app = FastAPI(lifespan=lifespan)
app.include_router(router=inventory_router)

@app.get("/")
async def root():
    return {"message": "Hello World"}

