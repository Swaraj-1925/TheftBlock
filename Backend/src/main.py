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
    print("\n=== Initializing Database and Tables ===")
    await create_db_and_tables()

    async for session in get_session():
        print("\n=== Step 1: Creating Suppliers and Products ===")
        supplier_mgr = SupplierManager(session)
        supplier1_products, supplier1_receipt_id = await supplier_mgr.create_random_products(
            supplier_id="SUPPLIER_001", supplier_name="Supplier One", count=3
        )
        supplier2_products, supplier2_receipt_id = await supplier_mgr.create_random_products(
            supplier_id="SUPPLIER_002", supplier_name="Supplier Two", count=2
        )
        print(f"Supplier 1 Receipt ID: {supplier1_receipt_id}, Products: {supplier1_products}")
        print(f"Supplier 2 Receipt ID: {supplier2_receipt_id}, Products: {supplier2_products}")

        print("\n=== Step 2: Adding Products to Warehouse ===")
        warehouse_mgr = WarehouseManager(session)
        inventory_receipt1_id = await warehouse_mgr.add_product(supplier1_receipt_id)
        inventory_receipt2_id = await warehouse_mgr.add_product(supplier2_receipt_id)
        print(f"Warehouse Receipt IDs: {inventory_receipt1_id}, {inventory_receipt2_id}")

        print("\n=== Step 3: Detecting Theft (Supplier to Warehouse) ===")
        theft_detector = TheftDetectionManager(session)
        supplier1_theft_result = await theft_detector.detect_theft("supplier_to_warehouse", supplier1_receipt_id)
        supplier2_theft_result = await theft_detector.detect_theft("supplier_to_warehouse", supplier2_receipt_id)
        print(f"Supplier 1 Theft Detection: {supplier1_theft_result}")
        print(f"Supplier 2 Theft Detection: {supplier2_theft_result}")

        print("\n=== Step 4: Simulating Warehouse to Consumer Dispatch ===")
        sensor1 = UHF_RFID(supplier1_products[0].rfid_tag)
        sensor2 = UHF_RFID(supplier2_products[0].rfid_tag)

        print(f"\n--- Dispatching Product: {await sensor1.get_sensor_id()} ---")
        sensor1.set_range(1.5)
        print(f"Initial Scan: {await sensor1.scan_item(session)}")
        await sensor1.mark_as_sold(session)
        print(f"Sold Confirmation: {await sensor1.is_sold(session)}")
        print(f"Final Read: {await sensor1.read_sensor(session)}")

        print(f"\n--- Dispatching Product Without Sale Confirmation: {await sensor2.get_sensor_id()} ---")

        print("\n=== Step 5: Detecting Theft (Warehouse to Consumer) ===")
        consumer_theft_result = await theft_detector.detect_theft("warehouse_to_consumer", "SHELF_001")
        print(f"Theft Check Result: {consumer_theft_result}")

        print("\n=== Step 6: Detecting Shelf Theft (Periodic Checks) ===")
        await theft_detector.detect_shelf_theft("SHELF_001", check_interval_seconds=2, max_checks=3)
        print(f"\nFinal Sensor Read (Unsold Product): {await sensor2.read_sensor(session)}")


if __name__ == "__main__":
    asyncio.run(main())