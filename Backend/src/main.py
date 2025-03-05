# Backend/src/main.py
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel
from Backend.src.dummy.uhf_rfid import UHF_RFID
from Backend.src.Db.db import get_session, async_engine

async def create_db_and_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async def main():
    await create_db_and_tables()  # Ensure tables exist
    print("Database and tables initialized.")
    async for session in get_session():
        sensor1 = UHF_RFID()
        sensor_id = await sensor1.init_sensor(session)
        print(f"Initialized sensor ID: {sensor_id}")

        sensor1.set_range(1.5)
        sensor1.set_range(3)

        print(f"Initial scan: {await sensor1.scan_item(session)}")
        await sensor1.mark_as_sold(session)
        print(f"Is sold? {await sensor1.is_sold(session)}")
        print(f"Full read: {await sensor1.read_sensor(session)}")

        sensor2 = UHF_RFID()
        await sensor2.init_sensor(session)
        print(f"Second sensor read: {await sensor2.read_sensor(session)}")

if __name__ == "__main__":
    asyncio.run(main())