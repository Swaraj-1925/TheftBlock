
import asyncio
from datetime import datetime, timedelta
from Backend.src.Db.database_management import DatabaseManagement
from Backend.src.Db.models import ShelfInventory, Sale, Product, Supplier, Shelf

async def simulate_data_insertion(db: DatabaseManagement):
    """Simulate real-time data insertion for hackathon demo."""
    base_time = datetime(2025, 3, 5, 10, 0)
    for i in range(10):
        time = base_time + timedelta(minutes=i * 5)
        if i % 3 == 0:  
            shelf_inv = ShelfInventory(
                shelf_inventory_id=f"SI{i+10}", 
                shelf_id="S1", 
                product_id="P1", 
                added_timestamp=base_time, 
                removed_timestamp=time
            )
        else:
            shelf_inv = ShelfInventory(
                shelf_inventory_id=f"SI{i+10}", 
                shelf_id="S1", 
                product_id="P1", 
                added_timestamp=time, 
                removed_timestamp=None
            )
            sale = Sale(sale_id=f"S{i+10}", product_id="P1", sale_timestamp=time)
            await db.insert(sale)
        await db.insert(shelf_inv)
        await asyncio.sleep(2)  