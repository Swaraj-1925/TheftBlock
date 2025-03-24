from typing import List, Dict, Any, Optional

from fastapi import HTTPException,status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from ..res_models import InventoryResponse, InventoryOwnerResponse, InventoryDetailsResponse, \
    StorageRackResponse, ShelfResponse, ProductResponse, SupplierResponse, InventoryStatisticsResponse, \
    ProductDetailsResponse
from src.Db.models import InventoryOwner, Inventory, Supplier, InventorySupplier, StorageRack, Shelf, Product, \
    ProductStatus
from src.manager.warehouse_manager import WarehouseManager


async def get_list_all_inventories(session: AsyncSession) -> List[InventoryResponse]:
    """Fetch a list of all inventories with basic information"""
    try:
        query = (
            select(Inventory, InventoryOwner)
            .join(InventoryOwner, Inventory.owner_id == InventoryOwner.owner_id)
        )
        result = await session.exec(query)
        inventory_owner_pairs = result.all()

        if not inventory_owner_pairs:
            raise HTTPException(
                status_code=status.HTTP_204_NO_CONTENT,
                detail="No inventories found. Try creating an inventory first."
            )

        inventory_details = [
            InventoryResponse(
                inventory_id=inventory.inventory_id,
                owner=InventoryOwnerResponse(
                    owner_id=owner.owner_id,
                    owner_name=owner.owner_name
                ),
                location=inventory.location,
                previous_theft_count=inventory.previous_theft_count
            )
            for inventory, owner in inventory_owner_pairs
        ]

        return inventory_details

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching inventory list: {str(e)}"
        )


async def get_inventory_details(session: AsyncSession, inventory_id: str) -> InventoryDetailsResponse:
    """Get detailed information about a specific inventory using WarehouseManager"""
    try:
        # Use the warehouse manager to get basic inventory information
        warehouse_manager = WarehouseManager(session)

        # First check if inventory exists
        inventory_query = (
            select(Inventory, InventoryOwner)
            .join(InventoryOwner, Inventory.owner_id == InventoryOwner.owner_id)
            .where(Inventory.inventory_id == inventory_id)
        )
        inventory_result = await session.exec(inventory_query)
        inventory_data = inventory_result.first()

        if not inventory_data:
            raise HTTPException(status_code=404, detail=f"Inventory with ID {inventory_id} not found")

        inventory, owner = inventory_data

        # Fetch inventory statistics to get most of the needed data in one call
        inventory_stats = await warehouse_manager.get_inventory_statistics(inventory_id)

        # Get suppliers for this inventory
        supplier_query = (
            select(Supplier)
            .join(InventorySupplier, Supplier.supplier_id == InventorySupplier.supplier_id)
            .where(InventorySupplier.inventory_id == inventory_id)
        )
        supplier_result = await session.exec(supplier_query)
        suppliers = supplier_result.all()

        # Format rack data from the statistics
        rack_details = [
            StorageRackResponse(
                rack_id=rack.rack_id,
                rack_location=rack.rack_location,
                shelf_count=len([s for s in inventory_stats.get('all_shelves', []) if s.rack_id == rack.rack_id])
            )
            for rack in inventory_stats.get('racks', [])
        ]

        supplier_responses = [
            SupplierResponse(supplier_id=s.supplier_id, supplier_name=s.supplier_name)
            for s in suppliers
        ]

        # Build the response
        return InventoryDetailsResponse(
            inventory_id=inventory.inventory_id,
            location=inventory.location,
            previous_theft_count=inventory.previous_theft_count,
            owner=InventoryOwnerResponse(
                owner_id=owner.owner_id,
                owner_name=owner.owner_name
            ),
            suppliers=supplier_responses,
            racks=rack_details,
            total_products=inventory_stats.get('products_on_shelf')
        )
    except HTTPException as e:
        print(f"Error get_inventory_details: {e} ")
        raise
    except Exception as e:
        print(f"Error get_inventory_details: {e} ")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching inventory details: {str(e)}"
        )


async def get_inventory_statistics(inventory_id: str, session: AsyncSession) -> InventoryStatisticsResponse:
    """Get statistical information about an inventory using WarehouseManager"""
    try:
        warehouse_manager = WarehouseManager(session)
        inventory_stats = await warehouse_manager.get_inventory_statistics(inventory_id)

        if not inventory_stats:
            raise HTTPException(status_code=404, detail=f"Inventory with ID {inventory_id} not found")

        # Get owner data
        owner = inventory_stats.get('owner', None)
        if not owner:
            # Fallback query if owner isn't in the stats (should be there)
            inventory_result = await session.exec(
                select(Inventory).where(Inventory.inventory_id == inventory_id)
            )
            inventory = inventory_result.first()

            if not inventory:
                raise HTTPException(status_code=404, detail=f"Inventory with ID {inventory_id} not found")

            owner_query = select(InventoryOwner).where(InventoryOwner.owner_id == inventory.owner_id)
            owner_result = await session.exec(owner_query)
            owner = owner_result.first()

        # Build owner response
        owner_data = InventoryOwnerResponse(
            owner_id=owner.owner_id,
            owner_name=owner.owner_name,
        )

        # Build the full statistics response
        return InventoryStatisticsResponse(
            inventory_id=inventory_stats['inventory_id'],
            location=inventory_stats['location'],
            owner=owner_data,
            previous_theft_count=inventory_stats['theft_count'],
            total_racks=len(inventory_stats['racks']),
            total_shelves=inventory_stats['total_shelves'],
            products_on_shelf=inventory_stats['products_on_shelf'],
            total_shelf_value=inventory_stats['total_shelf_value'],
            total_sales=inventory_stats['total_sales'],
            total_sales_value=inventory_stats['total_sales_value'],
            total_receipts=inventory_stats['total_receipts'],
            missing_products=inventory_stats['missing_products'],
            estimated_loss_value=inventory_stats['missing_products'],
            sale=[sale.dict() for sale in inventory_stats["sale"]]

        )
    except HTTPException:
        raise
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching inventory statistics: {str(e)}"
        )


async def get_inventory_products(
        session: AsyncSession,
        inventory_id: str,
        status: Optional[str] = None
) -> ProductDetailsResponse:
    """Get all products in an inventory with optional filtering by status"""
    try:
        warehouse_manager = WarehouseManager(session)

        # Use warehouse_manager to verify the inventory exists
        inventory_stats = await warehouse_manager.get_inventory_statistics(inventory_id)
        if not inventory_stats:
            raise HTTPException(status_code=404, detail=f"Inventory with ID {inventory_id} not found")

        # Get all rack IDs in this inventory
        rack_ids = [rack.rack_id for rack in inventory_stats.get('racks', [])]

        # Get all shelf IDs in these racks
        shelf_ids = [shelf.shelf_id for shelf in inventory_stats.get('all_shelves', [])]

        # Query products based on shelf IDs and optional status
        query = (
            select(Product, Shelf, StorageRack)
            .join(Shelf, Product.shelf_id == Shelf.shelf_id)
            .join(StorageRack, Shelf.rack_id == StorageRack.rack_id)
            .where(Shelf.shelf_id.in_(shelf_ids))
        )

        if status:
            try:
                # Convert string status to enum if needed
                product_status = ProductStatus(status)
                query = query.where(Product.status == product_status)
            except ValueError:
                # If status is not a valid enum value
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid product status: {status}"
                )

        result = await session.exec(query)
        products_data = result.all()

        # Convert to response model
        products = [
            ProductResponse(
                product_id=product.product_id,
                rfid_tag=product.rfid_tag,
                product_name=product.product_name,
                status=product.status.value,  # Convert enum to string
                price=product.price,
                shelf_id=shelf.shelf_id,
                rack_id=rack.rack_id,
                supplier_id= product.supplier_id
            )
            for product, shelf, rack in products_data
        ]

        return ProductDetailsResponse(
            inventory_id=inventory_id,
            products=products,
            total_products=len(products)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching inventory products: {str(e)}"
        )


async def move_product_to_shelf(
        session: AsyncSession,
        product_id: str,
        target_shelf_id: str
) -> Dict[str, Any]:
    """Move a product to a different shelf"""
    try:
        warehouse_manager = WarehouseManager(session)

        # Verify product exists
        product_query = select(Product).where(Product.product_id == product_id)
        product = await session.exec(product_query).first()

        if not product:
            raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found")

        # Verify shelf exists
        shelf_query = select(Shelf).where(Shelf.shelf_id == target_shelf_id)
        shelf = await session.exec(shelf_query).first()

        if not shelf:
            raise HTTPException(status_code=404, detail=f"Shelf with ID {target_shelf_id} not found")

        # Create list with just this one product
        result = await warehouse_manager.place_products_on_shelves(
            inventory_id=None,  # Not needed as we're specifying the shelf directly
            product_ids=[product_id],
            auto_assign=False  # We're manually assigning the shelf
        )

        return {
            "product_id": product_id,
            "previous_shelf_id": product.shelf_id,
            "new_shelf_id": target_shelf_id,
            "status": "success"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error moving product: {str(e)}"
        )


async def scan_inventory_shelf(
        session: AsyncSession,
        shelf_id: str
) -> Dict[str, Any]:
    """Scan a shelf and get results"""
    try:
        warehouse_manager = WarehouseManager(session)

        # Verify shelf exists
        shelf_query = select(Shelf).where(Shelf.shelf_id == shelf_id)
        shelf = await session.exec(shelf_query).first()

        if not shelf:
            raise HTTPException(status_code=404, detail=f"Shelf with ID {shelf_id} not found")

        # Perform scan
        scan_record, found_products = await warehouse_manager.scan_shelf(shelf_id)

        return {
            "scan_id": scan_record.scan_id,
            "shelf_id": shelf_id,
            "scan_timestamp": scan_record.scan_timestamp,
            "products_found": len(found_products),
            "product_details": [
                {
                    "product_id": product.product_id,
                    "product_name": product.product_name,
                    "rfid_tag": product.rfid_tag
                }
                for product in found_products
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error scanning shelf: {str(e)}"
        )


async def sell_product(
        session: AsyncSession,
        product_id: str,
        inventory_id: str
) -> Dict[str, Any]:
    """Record a product sale"""
    try:
        warehouse_manager = WarehouseManager(session)

        # Verify product exists
        product_query = select(Product).where(Product.product_id == product_id)
        product = await session.exec(product_query).first()

        if not product:
            raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found")

        # Verify inventory exists
        inventory_query = select(Inventory).where(Inventory.inventory_id == inventory_id)
        inventory = await session.exec(inventory_query).first()

        if not inventory:
            raise HTTPException(status_code=404, detail=f"Inventory with ID {inventory_id} not found")

        # Record the sale
        sale = await warehouse_manager.record_product_sale(product_id, inventory_id)

        return {
            "sale_id": sale.sale_id,
            "product_id": product_id,
            "inventory_id": inventory_id,
            "sale_timestamp": sale.sale_timestamp,
            "status": "success"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error recording sale: {str(e)}"
        )


