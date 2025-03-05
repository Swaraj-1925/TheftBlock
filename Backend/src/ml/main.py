
import asyncio
from Backend.src.Db.database_management import DatabaseManagement
from Backend.src.Db.db import get_session
from Backend.src.ml.anomaly_detection import detect_anomalies
from Backend.src.ml.data_simulator import simulate_data_insertion
from Backend.src.Db.models import Product, Supplier, Shelf

async def main():
    
    async for session in get_session():
        db = DatabaseManagement(session)
        
        await db.insert(Product(product_id="P1", rfid_tag="RFID1", product_name="Rice 5kg", status="available", supplier_id="SUP1"))
        await db.insert(Product(product_id="P2", rfid_tag="RFID2", product_name="Toothpaste", status="available", supplier_id="SUP1"))
        await db.insert(Supplier(supplier_id="SUP1", supplier_name="Supplier A"))
        await db.insert(Shelf(shelf_id="S1", shelf_location="Aisle 1, Shelf 2"))
        
    
        sim_task = asyncio.create_task(simulate_data_insertion(db))
        detect_task = asyncio.create_task(detect_anomalies(db, interval_seconds=10)) 
        
        await sim_task
        await detect_task

if __name__ == "__main__":
    asyncio.run(main())