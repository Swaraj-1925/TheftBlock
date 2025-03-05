# Backend/src/main.py
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel
from Backend.src.dummy.uhf_rfid import UHF_RFID
from Backend.src.dummy.product_manager import ProductManager
from Backend.src.Db.db import get_session, async_engine

async def create_db_and_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async def main():
    await create_db_and_tables()
    print("Database and tables initialized.")

    async for session in get_session():
        # Step 1: Create products with suppliers
        product_mgr = ProductManager()
        product1 = await product_mgr.create_product(
            product_id="PRODUCT_003",
            product_name="Widget A",
            supplier_id="SUPPLIER_001",
            session=session
        )
        product2 = await product_mgr.create_product(
            product_id="PRODUCT_004",
            product_name="Widget B",
            supplier_id="SUPPLIER_002",
            session=session
        )

        # Step 2: Initialize sensors with product RFID tags
        sensor1 = UHF_RFID(product1.rfid_tag)
        sensor2 = UHF_RFID(product2.rfid_tag)

        # Step 3: Simulate sensor operations
        print(f"Initialized sensor ID: {await sensor1.get_sensor_id()}")
        sensor1.set_range(1.5)
        print(f"Initial scan: {await sensor1.scan_item(session)}")
        await sensor1.mark_as_sold(session)
        print(f"Is sold? {await sensor1.is_sold(session)}")
        print(f"Full read: {await sensor1.read_sensor(session)}")

        print(f"Second sensor read: {await sensor2.read_sensor(session)}")

if __name__ == "__main__":
    asyncio.run(main())