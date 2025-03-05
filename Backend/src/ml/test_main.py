# Backend/src/ml/test_main.py
import asyncio
import pandas as pd
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
from Backend.src.Db.db import async_engine, get_session  # Use actual database engine
from Backend.src.Db.database_management import DatabaseManagement
from .anomaly_detection import detect_anomalies

async def main():
    # Use the actual database engine (no need to initialize tables here, handled in src/main.py)
    async for session in get_session():
        db = DatabaseManagement(session)
        
        # Run anomaly detection with a 48-hour window
        result_df = await detect_anomalies(db, interval_seconds=172800)  # 48 hours
        
        # Filter anomalies and select desired columns
        if not result_df.empty:
            anomalies = result_df[result_df["is_anomaly"]][["product_id", "product_name", "shelf_location"]]
            print(anomalies if not anomalies.empty else "No anomalies detected.")
        else:
            print("No data returned from anomaly detection.")

if __name__ == "__main__":
    asyncio.run(main())