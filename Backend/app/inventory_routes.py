from fastapi import APIRouter, Depends, HTTPException, Query
from watchfiles import awatch

from .res_models import InventoryDetailsResponse, InventoryStatisticsResponse, InventoryResponse, \
    ProductDetailsResponse
from .services.inventorie import get_list_all_inventories, get_inventory_details, get_inventory_statistics, \
    get_inventory_products
from src.Db.db import get_session
from sqlmodel.ext.asyncio.session import AsyncSession

inventory_router = APIRouter(prefix="/inventory",tags=["inventory"])

@inventory_router.get("/", response_model=list[InventoryResponse], description="Get all inventories")
async def fetch_all_inventories(session: AsyncSession = Depends(get_session)):
    """Get a list of all inventories with basic details"""
    return await get_list_all_inventories(session)

@inventory_router.get("/{inventory_id}", response_model=InventoryDetailsResponse,description="Get a specific inventory details")
async def fetch_inventory_details(inventory_id: str, session: AsyncSession = Depends(get_session)):
    """Get detailed information about a specific inventory including racks, shelves and products"""
    return await get_inventory_details(session, inventory_id)

@inventory_router.get("/{inventory_id}/statistics", response_model=InventoryStatisticsResponse,description="get statistics fo specific inventory")
async def fetch_inventory_statistics(inventory_id: str, session: AsyncSession = Depends(get_session)):
    """Get statistical information about an inventory"""
    return await get_inventory_statistics(inventory_id, session)

@inventory_router.get("/{inventory_id}/products", response_model=ProductDetailsResponse, description="get all Product stored in specific inventory")
async def fetch_inventory_products(
    inventory_id: str,
    status: str = None,
    session: AsyncSession = Depends(get_session)
):
    """Get all products in an inventory with optional filtering by status"""
    return await get_inventory_products(session, inventory_id, status)