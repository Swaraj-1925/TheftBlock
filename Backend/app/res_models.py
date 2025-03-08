# res_models.py
import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

from Backend.src.Db.models import ProductStatus


# Base Models - These can be reused across different responses
class InventoryOwnerResponse(BaseModel):
    owner_id: str
    owner_name: str


class SupplierResponse(BaseModel):
    supplier_id: str
    supplier_name: str

class Sale(BaseModel):
    sale_id: str
    product_id: str
    inventory_id: str
    sale_timestamp: datetime.datetime

class ProductResponse(BaseModel):
    product_id: str
    rfid_tag: str
    product_name: str
    status: str  # Using string instead of enum for better API compatibility
    price: float
    shelf_id: Optional[str] = None
    rack_id: Optional[str] = None


class ShelfResponse(BaseModel):
    shelf_id: str
    shelf_location: str
    product_count: int = Field(description="Number of products on the shelf")


class StorageRackResponse(BaseModel):
    rack_id: str
    rack_location: str
    shelf_count: int = Field(description="Number of shelves in the rack")


# Main Response Models
class InventoryResponse(BaseModel):
    """Basic inventory information"""
    inventory_id: str
    owner: InventoryOwnerResponse
    location: str
    previous_theft_count: int


class InventoryDetailsResponse(InventoryResponse):
    """Detailed inventory information including racks and shelves"""
    suppliers: List[SupplierResponse]
    racks: List[StorageRackResponse]
    total_products: int = Field(description="Total number of products in the inventory")


class ProductDetailsResponse(BaseModel):
    """Response for products in an inventory"""
    inventory_id: str
    products: List[ProductResponse]
    total_products: int = Field(description="Total number of products returned")


class InventoryStatisticsResponse(BaseModel):
    """Statistical information about an inventory"""
    inventory_id: str
    location: str
    owner: InventoryOwnerResponse
    previous_theft_count: int

    # Inventory structure stats
    total_racks: int
    total_shelves: int

    # Product stats
    products_on_shelf: int
    total_shelf_value: float
    missing_products: int
    estimated_loss_value: float

    # Sales and receipts stats
    total_sales: int
    total_sales_value: float
    total_receipts: int
    sale:List[Sale]