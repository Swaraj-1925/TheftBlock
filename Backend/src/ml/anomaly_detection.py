# Backend/src/ml/anomaly_detection.py
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from .data_fetcher import fetch_recent_data
from ..Db.database_management import DatabaseManagement

async def detect_anomalies(db: DatabaseManagement, interval_seconds: int = 60, contamination: float = 0.1):
    """Detect anomalies in the recent inventory and sales data using Isolation Forest."""
    time_window_minutes = interval_seconds / 60
    
    df = await fetch_recent_data(db, time_window_minutes)
    # print("Data fetched for anomaly detection:", df)

    if df.empty:
        # print("No data available for anomaly detection.")
        return df

    features = ["inventory_count", "inventory_change", "sales_count"]
    X = df[features].values

    iso_forest = IsolationForest(
        contamination=contamination,
        random_state=42,
        n_estimators=100
    )
    iso_forest.fit(X)

    df["anomaly_label"] = iso_forest.predict(X)
    df["anomaly_score"] = iso_forest.decision_function(X)
    df["is_anomaly"] = df["anomaly_label"].apply(lambda x: True if x == -1 else False)

    # print("Data with anomaly labels and scores:", df)
    return df