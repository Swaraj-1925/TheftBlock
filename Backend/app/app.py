from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List, Optional
from sqlalchemy import select
import asyncio
from fastapi.responses import JSONResponse
from fastapi import Request
from Backend.src.Db.db import  get_session
from Backend.src.dummy.uhf_rfid import UHF_RFID
from Backend.src.main import create_db_and_tables
from Backend.src.Db.models import (
    Supplier, Product, SupplierReceipt, SupplierReceiptItem,
    InventoryReceipt, InventoryReceiptItem, Shelf, ShelfInventory,
    Sale, ShelfScan, ShelfScanItem
)
from Backend.src.manager.supplier_manager import SupplierManager
from Backend.src.manager.warehouse_manager import WarehouseManager
from Backend.src.manager.theft_detection_manager import TheftDetectionManager
from fastapi.middleware.cors import CORSMiddleware

class SupplierCreateRequest(BaseModel):
    supplier_id: str
    supplier_name: str
    product_count: int

app = FastAPI(title="Inventory Management API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","http://localhost:3000","http://localhost:8000"],  # Default Vite port for your React app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.on_event("startup")
async def on_startup():
    await create_db_and_tables()


@app.exception_handler(ValueError)
async def value_error_exception_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,  # or 404, depending on your use case
        content={"detail": str(exc)},
    )
@app.get("/api/shelf-inventory", response_model=List[dict])
async def get_shelf_inventory(session: AsyncSession = Depends(get_session)):
    stmt = (
        select(ShelfInventory, Shelf)
        .join(Shelf, Shelf.shelf_id == ShelfInventory.shelf_id)
    )
    result = await session.exec(stmt)
    shelves = result.all()
    print(f"Retrieved {len(shelves)} shelves")
    return [
        {
            "shelf_inventory_id": shelf_inv.shelf_inventory_id,
            "shelf_location": shelf.shelf_location
        }
        for shelf_inv, shelf in shelves
    ]
@app.get("/api/shelf-inventory/{shelf_inventory_id}/products", response_model=List[Product])
async def get_products_by_shelf(shelf_inventory_id: str, session: AsyncSession = Depends(get_session)):
    stmt = (
        select(Product)
        .join(ShelfInventory, ShelfInventory.product_id == Product.product_id)
        .where(ShelfInventory.shelf_inventory_id == shelf_inventory_id)
        .where(ShelfInventory.removed_timestamp.is_(None))
    )
    result = await session.exec(stmt)
    products = result.all()
    if not products:
        return []
    return products
@app.get("/api/metrics", response_model=dict)
async def get_metrics(session: AsyncSession = Depends(get_session)):
    # Total Items Received
    stmt_received = select(InventoryReceipt.total_products_received)
    received_result = await session.exec(stmt_received)
    total_received = sum(r or 0 for r in received_result.all())

    # Total Items Sold
    stmt_sold = select(Sale)
    sold_result = await session.exec(stmt_sold)
    total_sold = len(sold_result.all())

    # Total Items in Inventory
    stmt_inventory = (
        select(Product)
        .where(Product.status == "available")
    )
    inventory_result = await session.exec(stmt_inventory)
    total_inventory = len(inventory_result.all())

    # Missing Items
    theft_manager = TheftDetectionManager(session)
    shelf_ids = [shelf.shelf_id for shelf in (await session.exec(select(Shelf))).all()]
    missing_items = 0
    for shelf_id in shelf_ids:
        result = await theft_manager.detect_theft("warehouse_to_consumer", shelf_id)
        missing_items += result["discrepancy"]

    return {
        "totalReceived": total_received,
        "totalSold": total_sold,
        "totalInventory": total_inventory,
        "missingItems": missing_items
    }
@app.post("/api/supplier/create", response_model=dict)
async def create_supplier_and_products(
    supplier: SupplierCreateRequest,
    session: AsyncSession = Depends(get_session)
):
    supplier_manager = SupplierManager(session)
    products, receipt_id = await supplier_manager.create_random_products(
        supplier.supplier_id, supplier.supplier_name, supplier.product_count
    )
    return {
        "supplier_id": supplier.supplier_id,
        "receipt_id": receipt_id,
        "products_created": len(products)
    }
@app.post("/api/warehouse/receive/{supplier_receipt_id}", response_model=dict)
async def receive_products(
    supplier_receipt_id: str,
    session: AsyncSession = Depends(get_session)
):
    warehouse_manager = WarehouseManager(session)
    inventory_receipt_id = await warehouse_manager.add_product(supplier_receipt_id)
    return {"inventory_receipt_id": inventory_receipt_id}


# --- Mark Product as Sold ---
@app.post("/api/product/mark-sold/{rfid_tag}")
async def mark_product_sold(rfid_tag: str, session: AsyncSession = Depends(get_session)):
    rfid_sensor = UHF_RFID(rfid_tag)
    await rfid_sensor.mark_as_sold(session)
    return {"message": f"Product with RFID {rfid_tag} marked as sold"}

# --- Scan Shelf (for testing) ---
@app.get("/api/shelf/scan/{shelf_id}", response_model=List[str])
async def scan_shelf(shelf_id: str, session: AsyncSession = Depends(get_session)):
    # Use any existing RFID tag for the sensor simulation
    stmt = select(Product.rfid_tag).limit(1)
    result = await session.exec(stmt)
    rfid_tag = result.first() or "RFID_DEFAULT"
    rfid_sensor = UHF_RFID(rfid_tag)
    detected_rfids = await rfid_sensor.scan_shelf(session, shelf_id)
    return detected_rfids

# --- Theft Detection ---
@app.get("/api/theft/{stage}/{source_id}", response_model=dict)
async def detect_theft(stage: str, source_id: str, session: AsyncSession = Depends(get_session)):
    theft_manager = TheftDetectionManager(session)
    result = await theft_manager.detect_theft(stage, source_id)
    return result


