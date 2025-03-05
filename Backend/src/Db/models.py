from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

# Suppliers' table
class Supplier(SQLModel, table=True):
    supplier_id: str = Field(default=None, primary_key=True)
    supplier_name: str

# Products table
class Product(SQLModel, table=True):
    product_id: str = Field(default=None, primary_key=True)
    rfid_tag: str = Field(unique=True)  # Unique RFID tag for each product
    product_name: str
    status: str = Field(default="available")  # e.g., "available" or "sold"
    supplier_id: str = Field(foreign_key="supplier.supplier_id")


# Supplier Receipts table
class SupplierReceipt(SQLModel, table=True):
    receipt_id: str = Field(default=None, primary_key=True)
    supplier_id: str = Field(foreign_key="supplier.supplier_id")
    date_sent: datetime
    total_products_sent: int

# Supplier Receipt Items table (products in supplier receipt)
class SupplierReceiptItem(SQLModel, table=True):
    receipt_item_id: str= Field(default=None, primary_key=True)
    receipt_id: str = Field(foreign_key="supplierreceipt.receipt_id")
    product_id: str = Field(foreign_key="product.product_id")

# Inventory Receipts table
class InventoryReceipt(SQLModel, table=True):
    receipt_id: str = Field(default=None, primary_key=True)
    supplier_receipt_id: str = Field(foreign_key="supplierreceipt.receipt_id")  # Links to supplier receipt
    date_received: datetime
    total_products_received: int

# Inventory Receipt Items table (products received in inventory)
class InventoryReceiptItem(SQLModel, table=True):
    receipt_item_id: str = Field(default=None, primary_key=True)
    receipt_id: str = Field(foreign_key="inventoryreceipt.receipt_id")
    product_id: str = Field(foreign_key="product.product_id")

# Shelves table
class Shelf(SQLModel, table=True):
    shelf_id: str = Field(default=None, primary_key=True)
    shelf_location: str  # e.g., "Aisle 1, Shelf 2"

# Shelf Inventory table (tracks products on shelves)
class ShelfInventory(SQLModel, table=True):
    shelf_inventory_id: str = Field(default=None, primary_key=True)
    shelf_id: str = Field(foreign_key="shelf.shelf_id")
    product_id: str = Field(foreign_key="product.product_id")
    added_timestamp: datetime  # When product was placed on shelf
    removed_timestamp: Optional[datetime] = None  # When product was sold/removed

# Sales table (products scanned and sold)
class Sale(SQLModel, table=True):
    sale_id: str = Field(default=None, primary_key=True)
    product_id: str = Field(foreign_key="product.product_id")
    sale_timestamp: datetime

# Shelf Scans table (periodic scans)
class ShelfScan(SQLModel, table=True):
    scan_id: str = Field(default=None, primary_key=True)
    shelf_id: str = Field(foreign_key="shelf.shelf_id")
    scan_timestamp: datetime

# Shelf Scan Items table (products detected in scans)
class ShelfScanItem(SQLModel, table=True):
    scan_item_id: str = Field(default=None, primary_key=True)
    scan_id: str = Field(foreign_key="shelfscan.scan_id")
    product_id: str = Field(foreign_key="product.product_id")
