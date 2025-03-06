from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Dict, List

from Backend.app.model import SupplierCreate
from Backend.src.manager.supplier_manager import SupplierManager
from Backend.src.manager.warehouse_manager import WarehouseManager
from Backend.src.manager.theft_detection_manager import TheftDetectionManager
from Backend.src.Db.models import Supplier, Product
from Backend.src.main import get_session

router = APIRouter()


@router.post("/suppliers", response_model=Supplier)
async def create_supplier(
    supplier_data: SupplierCreate,
    session: AsyncSession = Depends(get_session)
):
    print(f"Creating supplier: {supplier_data.supplier_id}, {supplier_data.supplier_name}")
    manager = SupplierManager(session)
    supplier = await manager.create_supplier(supplier_data.supplier_id, supplier_data.supplier_name)
    return supplier


# Receive Products
@router.post("/receive-products/", response_model=dict)
async def receive_products(
        supplier_id: str,
        supplier_name: str,
        product_count: int,
        session: AsyncSession = Depends(get_session)
):
    supplier_manager = SupplierManager(session)
    warehouse_manager = WarehouseManager(session)

    # Create supplier and random products
    products, supplier_receipt_id = await supplier_manager.create_random_products(
        supplier_id, supplier_name, product_count
    )

    # Add products to warehouse
    inventory_receipt_id = await warehouse_manager.add_product(supplier_receipt_id)

    return {
        "supplier_receipt_id": supplier_receipt_id,
        "inventory_receipt_id": inventory_receipt_id,
        "products_received": len(products)
    }


# Mark as Sold
@router.post("/mark-sold/", response_model=dict)
async def mark_sold(
        product_id: str,
        session: AsyncSession = Depends(get_session)
):
    from Backend.src.Db.models import Sale, ShelfInventory
    import datetime

    warehouse_manager = WarehouseManager(session)
    product = await warehouse_manager.db.search(Product, all_results=False, product_id=product_id)

    if not product or product.status != "available":
        raise HTTPException(status_code=400, detail="Product not available or not found")

    # Update product status
    product.status = "sold"
    await warehouse_manager.db.update(product)

    # Record sale
    sale_id = f"SALE_{hashlib.sha256(str(datetime.datetime.now()).encode()).hexdigest()[:10]}"
    sale = Sale(
        sale_id=sale_id,
        product_id=product_id,
        sale_timestamp=datetime.datetime.now()
    )
    await warehouse_manager.db.insert(sale)

    # Update shelf inventory
    shelf_item = await warehouse_manager.db.search(
        ShelfInventory, all_results=False, product_id=product_id, removed_timestamp=None
    )
    if shelf_item:
        shelf_item.removed_timestamp = datetime.datetime.now()
        await warehouse_manager.db.update(shelf_item)

    return {"message": f"Product {product_id} marked as sold", "sale_id": sale_id}


# Scan Shelves
@router.post("/scan-shelves/", response_model=dict)
async def scan_shelves(
        shelf_id: str,
        session: AsyncSession = Depends(get_session)
):
    theft_manager = TheftDetectionManager(session)
    result = await theft_manager.detect_shelf_theft(shelf_id=shelf_id)
    return {"shelf_id": shelf_id, "theft_result": "Check console for detailed output"}