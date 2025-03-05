# Backend/src/ml/data_fetcher.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy.sql import text
from Backend.src.Db.database_management import DatabaseManagement
from Backend.src.Db.models import Product, ShelfInventory, Sale, Shelf

async def fetch_recent_data(db: DatabaseManagement, time_window_minutes: int = 60) -> pd.DataFrame:
    """Fetch recent shelf inventory and sales data from the database."""
    cutoff_time = datetime.now() - timedelta(minutes=time_window_minutes)
    # print(f"Cutoff Time: {cutoff_time}")

    # Fetch Shelf Inventory
    shelf_inv_query = text("""
    SELECT shelf_inventory_id, product_id, shelf_id, added_timestamp, removed_timestamp
    FROM ShelfInventory
    WHERE added_timestamp >= :cutoff OR removed_timestamp >= :cutoff
    ORDER BY added_timestamp, removed_timestamp
    """).bindparams(cutoff=cutoff_time)
    shelf_inv_results = await db.session.exec(shelf_inv_query)
    shelf_inv_df = pd.DataFrame(shelf_inv_results.mappings().all()) if shelf_inv_results else pd.DataFrame()
    # print("Raw Shelf Inventory DataFrame:", shelf_inv_df)

    # Fetch Sales
    sales_query = text("""
    SELECT product_id, sale_timestamp, COUNT(*) as sales_count
    FROM Sale
    WHERE sale_timestamp >= :cutoff
    GROUP BY product_id, sale_timestamp
    """).bindparams(cutoff=cutoff_time)
    sales_results = await db.session.exec(sales_query)
    sales_df = pd.DataFrame(sales_results.mappings().all()) if sales_results else pd.DataFrame()
    # print("Raw Sales DataFrame:", sales_df)

    # Fetch Products
    products = await db.search(Product, all_results=True)
    products_df = pd.DataFrame([p.dict() for p in products])
    # print("Products DataFrame:", products_df)

    # Fetch Shelves
    shelves = await db.search(Shelf, all_results=True)
    shelves_df = pd.DataFrame([s.dict() for s in shelves])
    # print("Shelves DataFrame:", shelves_df)

    # Preprocess Shelf Inventory Data
    if not shelf_inv_df.empty:
        shelf_inv_df["stock_change"] = np.where(shelf_inv_df["added_timestamp"].notnull() & shelf_inv_df["removed_timestamp"].isnull(), 1,
                                                np.where(shelf_inv_df["removed_timestamp"].notnull(), -1, 0))
        shelf_inv_df["timestamp"] = shelf_inv_df.apply(
            lambda row: row["removed_timestamp"] if pd.notnull(row["removed_timestamp"]) else row["added_timestamp"], axis=1
        )
        shelf_inv_df = shelf_inv_df.groupby(["product_id", "shelf_id", "timestamp"])["stock_change"].sum().reset_index()
        shelf_inv_df["inventory_count"] = shelf_inv_df.groupby("product_id")["stock_change"].cumsum().fillna(0)
        shelf_inv_df["inventory_change"] = shelf_inv_df.groupby("product_id")["inventory_count"].diff().fillna(0)
        # print("After Preprocessing Shelf Inventory:", shelf_inv_df)

        shelf_inv_df = shelf_inv_df.merge(products_df[["product_id", "product_name"]], on="product_id", how="left")
        # print("After Merging Products:", shelf_inv_df)

        shelf_inv_df = shelf_inv_df.merge(shelves_df[["shelf_id", "shelf_location"]], on="shelf_id", how="left")
        # print("After Merging Shelves:", shelf_inv_df)

        if not sales_df.empty:
            shelf_inv_df = shelf_inv_df.merge(sales_df[["sale_timestamp", "product_id", "sales_count"]], 
                                              left_on=["timestamp", "product_id"], 
                                              right_on=["sale_timestamp", "product_id"], 
                                              how="left")
            # print("After Merging Sales:", shelf_inv_df)
        
        shelf_inv_df["sales_count"] = shelf_inv_df["sales_count"].fillna(0)
        # print("Final Shelf Inventory DataFrame Before Return:", shelf_inv_df)

    # Ensure the returned DataFrame has the expected columns, even if empty
    expected_columns = ["timestamp", "product_id", "product_name", "shelf_location", "inventory_count", "inventory_change", "sales_count"]
    if shelf_inv_df.empty:
        return pd.DataFrame(columns=expected_columns)
    return shelf_inv_df[expected_columns]