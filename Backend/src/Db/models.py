from sqlmodel import SQLModel, Field, Enum
from typing import Optional
from datetime import datetime
import enum

# Enum for product status
class ProductStatus(str, enum.Enum):
    SOLD = "sold"
    ON_SHELF = "on_shelf"
    OUT_SHELF = "out_shelf"
    MISSING = "missing"
    WITH_SUPPLIER ="with_supplier"

# Inventory Owners table
class InventoryOwner(SQLModel, table=True):
    owner_id: str = Field(default=None, primary_key=True)
    owner_name: str

# Inventories table
class Inventory(SQLModel, table=True):
    inventory_id: str = Field(default=None, primary_key=True)
    owner_id: str = Field(foreign_key="inventoryowner.owner_id")
    location: str  # Address/location of the inventory
    previous_theft_count: int = Field(default=0)

# Suppliers table
class Supplier(SQLModel, table=True):
    supplier_id: str = Field(default=None, primary_key=True)
    supplier_name: str

# Inventory-Supplier relationship (many-to-many)
class InventorySupplier(SQLModel, table=True):
    inventory_supplier_id: str = Field(default=None, primary_key=True)
    inventory_id: str = Field(foreign_key="inventory.inventory_id")
    supplier_id: str = Field(foreign_key="supplier.supplier_id")

# Storage Racks table
class StorageRack(SQLModel, table=True):
    rack_id: str = Field(default=None, primary_key=True)
    inventory_id: str = Field(foreign_key="inventory.inventory_id")
    rack_location: str  # e.g., "Section A, Rack 1"

# Shelves table
class Shelf(SQLModel, table=True):
    shelf_id: str = Field(default=None, primary_key=True)
    rack_id: str = Field(foreign_key="storagerack.rack_id")
    shelf_location: str  # e.g., "Level 1"

# Products table
class Product(SQLModel, table=True):
    product_id: str = Field(default=None, primary_key=True)
    rfid_tag: str = Field(unique=True)
    product_name: str
    status: ProductStatus = Field(default=ProductStatus.ON_SHELF)
    supplier_id: str = Field(foreign_key="supplier.supplier_id")
    shelf_id: Optional[str] = Field(default=None, foreign_key="shelf.shelf_id")
    price: float = Field(default=100.0)
    receipt_id: Optional[str] = Field(default=None, foreign_key="supplierreceipt.receipt_id")  # New field

# Supplier Receipts table
class SupplierReceipt(SQLModel, table=True):
    receipt_id: str = Field(default=None, primary_key=True)
    supplier_id: str = Field(foreign_key="supplier.supplier_id")
    inventory_id: str = Field(foreign_key="inventory.inventory_id")
    date_sent: datetime
    total_products_sent: int

# Supplier Receipt Items table
class SupplierReceiptItem(SQLModel, table=True):
    receipt_item_id: str = Field(default=None, primary_key=True)
    receipt_id: str = Field(foreign_key="supplierreceipt.receipt_id")
    product_id: str = Field(foreign_key="product.product_id")

# Inventory Receipts table
class InventoryReceipt(SQLModel, table=True):
    receipt_id: str = Field(default=None, primary_key=True)
    supplier_receipt_id: str = Field(foreign_key="supplierreceipt.receipt_id")
    inventory_id: str = Field(foreign_key="inventory.inventory_id")
    date_received: datetime
    total_products_received: int

# Inventory Receipt Items table
class InventoryReceiptItem(SQLModel, table=True):
    receipt_item_id: str = Field(default=None, primary_key=True)
    receipt_id: str = Field(foreign_key="inventoryreceipt.receipt_id")
    product_id: str = Field(foreign_key="product.product_id")

# Shelf Inventory table
class ShelfInventory(SQLModel, table=True):
    shelf_inventory_id: str = Field(default=None, primary_key=True)
    shelf_id: str = Field(foreign_key="shelf.shelf_id")
    product_id: str = Field(foreign_key="product.product_id")
    added_timestamp: datetime
    removed_timestamp: Optional[datetime] = None

# Sales table
class Sale(SQLModel, table=True):
    sale_id: str = Field(default=None, primary_key=True)
    product_id: str = Field(foreign_key="product.product_id")
    inventory_id: str = Field(foreign_key="inventory.inventory_id")
    sale_timestamp: datetime

# Shelf Scans table
class ShelfScan(SQLModel, table=True):
    scan_id: str = Field(default=None, primary_key=True)
    shelf_id: str = Field(foreign_key="shelf.shelf_id")
    scan_timestamp: datetime

# Shelf Scan Items table
class ShelfScanItem(SQLModel, table=True):
    scan_item_id: str = Field(default=None, primary_key=True)
    scan_id: str = Field(foreign_key="shelfscan.scan_id")
    product_id: str = Field(foreign_key="product.product_id")