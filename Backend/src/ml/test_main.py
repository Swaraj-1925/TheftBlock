# Backend/src/ml/test_main.py
import asyncio
import json
import pandas as pd
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
from .db_init import initialize_database
from ..Db.database_management import DatabaseManagement
from .anomaly_detection import detect_anomalies
from .data_simulator import simulate_data_insertion
from ..Db.models import Product, Supplier, Shelf, ShelfInventory, Sale

# In-memory SQLite engine for testing
test_engine = create_async_engine("sqlite+aiosqlite:///:memory:")

async def get_test_session() -> AsyncSession:
    """Provide a session for the in-memory SQLite database."""
    async_session = sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session

async def load_json_data(db: DatabaseManagement, json_file: str):
    """Load dummy data from JSON into the in-memory database."""
    with open(json_file, 'r') as f:
        data = json.load(f)

    # Insert Suppliers
    for supplier in data.get("Supplier", []):
        await db.insert(Supplier(**supplier))

    # Insert Products
    for product in data.get("Product", []):
        await db.insert(Product(**product))

    # Insert Shelves
    for shelf in data.get("Shelf", []):
        await db.insert(Shelf(**shelf))

    # Insert Shelf Inventory
    for shelf_inv in data.get("ShelfInventory", []):
        shelf_inv["added_timestamp"] = pd.to_datetime(shelf_inv["added_timestamp"])
        if shelf_inv["removed_timestamp"]:
            shelf_inv["removed_timestamp"] = pd.to_datetime(shelf_inv["removed_timestamp"])
        await db.insert(ShelfInventory(**shelf_inv))

    # Insert Sales
    for sale in data.get("Sale", []):
        sale["sale_timestamp"] = pd.to_datetime(sale["sale_timestamp"])
        await db.insert(Sale(**sale))

    # Commit the session
    await db.session.commit()

async def main():
    # Initialize in-memory database
    await initialize_database(test_engine)
    
    async for session in get_test_session():
        db = DatabaseManagement(session)
        
        # Load dummy data from JSON
        json_path = r"E:\TheftBlock\TheftBlock\Backend\dummy_data\warehouse_to_customer.json"
        await load_json_data(db, json_path)
        
        # Run anomaly detection with a 48-hour window
        result_df = await detect_anomalies(db, interval_seconds=172800)  # 48 hours
        
        # Filter anomalies and select only desired columns
        if not result_df.empty:
            anomalies = result_df[result_df["is_anomaly"]][["product_id", "product_name", "shelf_location"]]
            print(anomalies if not anomalies.empty else "No anomalies detected.")
        else:
            print("No data returned from anomaly detection.")

if __name__ == "__main__":
    asyncio.run(main())