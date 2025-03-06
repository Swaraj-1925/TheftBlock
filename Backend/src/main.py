# Backend/src/main.py
import hashlib
import datetime
import asyncio
import uuid

from sqlmodel import SQLModel
from Backend.src.dummy.uhf_rfid import UHF_RFID
from Backend.src.manager.supplier_manager import SupplierManager
from Backend.src.Db.db import get_session, async_engine
from Backend.src.manager.theft_detection_manager import TheftDetectionManager
from Backend.src.manager.warehouse_manager import WarehouseManager


async def create_db_and_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)
    print("Database and tables initialized.")

def generate_id(tag:str):
    unique_id = str(uuid.uuid4())
    timestamp = str(datetime.datetime.now())
    id_hash = hashlib.sha256((timestamp + unique_id).encode()).hexdigest()[:10]
    id_tag = f"{tag}_{id_hash}"
    return id_tag


async def main():
    await create_db_and_tables()

    async for session in get_session():
        # Step 1: Create suppliers and their products
        supplier_mgr = SupplierManager(session)
        supplier1_products, supplier1_receipt_id = await supplier_mgr.create_random_products(
            supplier_id="SUPPLIER_001", supplier_name="Supplier One", count=3
        )
        supplier2_products, supplier2_receipt_id = await supplier_mgr.create_random_products(
            supplier_id="SUPPLIER_002", supplier_name="Supplier Two", count=2
        )

        # Step 2: Warehouse receives products
        warehouse_mgr = WarehouseManager(session)
        inventory_receipt1_id = await warehouse_mgr.add_product(supplier1_receipt_id)
        inventory_receipt2_id = await warehouse_mgr.add_product(supplier2_receipt_id)

        # Step 3: Detect theft (Supplier to Warehouse)
        theft_detector = TheftDetectionManager(session)
        supplier1_theft_result = await theft_detector.detect_theft("supplier_to_warehouse", supplier1_receipt_id)
        supplier2_theft_result = await theft_detector.detect_theft("supplier_to_warehouse", supplier2_receipt_id)

        # Step 4: Simulate warehouse-to-consumer dispatch and sales
        sensor1 = UHF_RFID(supplier1_products[0].rfid_tag)
        sensor2 = UHF_RFID(supplier2_products[0].rfid_tag)

        print("\n--- Warehouse to Consumer Simulation ---")
        print(f"Dispatching product with sensor ID: {await sensor1.get_sensor_id()}")
        sensor1.set_range(1.5)
        print(f"Initial scan before dispatch: {await sensor1.scan_item(session)}")
        await sensor1.mark_as_sold(session)
        print(f"Product dispatched and sold? {await sensor1.is_sold(session)}")
        print(f"Full read after sale: {await sensor1.read_sensor(session)}")
        print(f"Dispatching product with sensor ID: {await sensor2.get_sensor_id()} but not confirming sale...")

        # Step 5: Detect theft (Warehouse to Consumer)
        consumer_theft_result = await theft_detector.detect_theft("warehouse_to_consumer", "SHELF_001")
        print(f"\nWarehouse to Consumer theft check result: {consumer_theft_result}")

        # Step 6: Detect shelf theft with periodic checks
        await theft_detector.detect_shelf_theft("SHELF_001", check_interval_seconds=2, max_checks=3)

        # Show second sensor read
        print(f"\nSecond sensor read (not sold): {await sensor2.read_sensor(session)}")

if __name__ == "__main__":
    asyncio.run(main())