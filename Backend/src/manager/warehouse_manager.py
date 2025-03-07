import asyncio
import datetime
import hashlib
import json
import random
from typing import Optional, List, Dict, Any, Tuple

from sqlmodel.ext.asyncio.session import AsyncSession
from Backend.src.Db.database_management import DatabaseManagement
from Backend.src.Db.models import Product, ShelfInventory, SupplierReceiptItem, SupplierReceipt, InventoryReceiptItem, \
    Shelf, InventoryReceipt, StorageRack, ProductStatus, Inventory, Sale, ShelfScan, InventoryOwner


class WarehouseManager:
    def __init__(self, session: AsyncSession, shelf_ids: Optional[list] = None):
        self.session = session
        self.shelf_ids = shelf_ids or [f"shelf_{i + 1}" for i in range(10)]
        self.db = DatabaseManagement(session)

    async def setup_inventory(self, inventory_id: str, owner_id: str, location: str) -> Inventory:
        inventory = await self.db.search(Inventory, all_results=False, inventory_id=inventory_id)
        if not inventory:
            owner = InventoryOwner(
                owner_id=owner_id,
                owner_name="Main Warehouse Owner"
            )
            await self.db.insert(owner)
            inventory = Inventory(
                inventory_id=inventory_id,
                owner_id=owner_id,
                location=location,
                previous_theft_count=0
            )
            await self.db.insert(inventory)
            print(f"Created inventory with ID: {inventory_id}")

            # Create default storage racks and shelves
            await self.setup_racks_and_shelves(inventory_id)

        return inventory

    async def setup_racks_and_shelves(self, inventory_id: str, rack_count: int = 2,num_shelf:int=4) -> List[StorageRack]:
        """Set up storage racks and shelves for an inventory"""
        racks = []
        for i in range(rack_count):
            rack_id = f"RACK_{i + 1:03d}"
            rack = await self.db.search(StorageRack, all_results=False, rack_id=rack_id)
            if not rack:
                rack = StorageRack(
                    rack_id=rack_id,
                    inventory_id=inventory_id,
                    rack_location=f"Section {chr(65 + i)}"  # A, B, C, etc.
                )
                await self.db.insert(rack)
                print(f"Created rack: {rack_id} in inventory {inventory_id}")

                for j in range(num_shelf):
                    shelf_id = f"SHELF_{i * 4 + j + 1:03d}"
                    shelf = await self.db.search(Shelf, all_results=False, shelf_id=shelf_id)
                    if not shelf:
                        shelf = Shelf(
                            shelf_id=shelf_id,
                            rack_id=rack_id,
                            shelf_location=f"Level {j + 1}"
                        )
                        await self.db.insert(shelf)
                        print(f"Created shelf: {shelf_id} on rack {rack_id}")

            racks.append(rack)
        return racks

    async def receive_products(self, supplier_receipt_id: str, inventory_id: str, loss_simulation: bool = False) -> str:
        """Receive products from a supplier receipt into inventory with optional loss simulation"""
        supplier_receipt = await self.db.search(SupplierReceipt, all_results=False, receipt_id=supplier_receipt_id)
        if not supplier_receipt:
            raise ValueError(f"Supplier receipt {supplier_receipt_id} not found!")

        receipt_hash = hashlib.sha256(str(datetime.datetime.now()).encode()).hexdigest()[:10]
        inventory_receipt_id = f"IR_{receipt_hash}"
        received_products = []

        supplier_items = await self.db.search(SupplierReceiptItem, all_results=True, receipt_id=supplier_receipt_id)

        # Get all products from the receipt
        for item in supplier_items:
            product = await self.db.search(Product, all_results=False, product_id=item.product_id)
            if not product:
                print(f"Warning: Product {item.product_id} not found in the database")
                continue

            if not loss_simulation or random.random() > 0.3:  # 70% chance of receiving or no simulation
                received_products.append(product)
                print(f"Received product: {product.product_id}, RFID: {product.rfid_tag}")
            else:
                print(f"***Simulated loss: {item.product_id} not received!***")
                await self.report_missing_product(product.product_id)

        inventory_receipt = InventoryReceipt(
            receipt_id=inventory_receipt_id,
            supplier_receipt_id=supplier_receipt_id,
            inventory_id=inventory_id,
            date_received=datetime.datetime.now(),
            total_products_received=len(received_products)
        )
        await self.db.insert(inventory_receipt)
        print(f"Created inventory receipt: {inventory_receipt_id}")

        # Create receipt items
        receipt_items = []
        for product in received_products:
            receipt_item_hash = hashlib.sha256(
                (str(datetime.datetime.now()) + product.product_id).encode()
            ).hexdigest()[:10]
            receipt_item_id = f"IRI_{receipt_item_hash}"

            receipt_item = InventoryReceiptItem(
                receipt_item_id=receipt_item_id,
                receipt_id=inventory_receipt_id,
                product_id=product.product_id
            )
            receipt_items.append(receipt_item)

            # Update product status using update_row
            search_criteria = {"product_id": product.product_id}
            update_data = {
                "product_id": product.product_id,
                "rfid_tag": product.rfid_tag,
                "product_name": product.product_name,
                "status": ProductStatus.OUT_SHELF,
                "supplier_id": product.supplier_id,
                "shelf_id": product.shelf_id,
                "price": product.price,
                "receipt_id": product.receipt_id
            }
            await self.db.update_row(Product, search_criteria, update_data)

        # Bulk insert receipt items
        # await asyncio.gather(*(self.db.insert(item) for item in receipt_items))
        try:
            # Use a context manager to ensure proper session handling
            async with self.session as session:
                for product in receipt_items:
                    await self.db.insert(product,auto_commit=False)  # Insert one at a time
                await session.commit()  # Commit once after all inserts
        except Exception as e:
            await self.session.rollback()
            raise Exception(f"Failed to insert products: {str(e)}")

        return inventory_receipt_id

    async def place_products_on_shelves(self, inventory_id: str, product_ids: List[str],
                                        auto_assign: bool = True) -> Dict[str, List[ShelfInventory]]:
        """Place products on shelves, optionally auto-assigning to available shelves"""
        # Get all shelves in this inventory
        racks = await self.db.search(StorageRack, all_results=True, inventory_id=inventory_id)
        if not racks:
            raise ValueError(f"No racks found in inventory {inventory_id}")
        rack_ids = [rack.rack_id for rack in racks]
        available_shelves = await self.db.search(Shelf, all_results=True, rack_id__in=rack_ids)
        if not available_shelves:
            raise ValueError(f"No available shelves found in inventory {inventory_id}")


        shelf_inventory_records = {}
        now = datetime.datetime.now()

        for product_id in product_ids:
            product = await self.db.search(Product, all_results=False, product_id=product_id)
            if not product:
                print(f"Warning: Product {product_id} not found")
                continue

            # Determine target shelf
            target_shelf = None
            if auto_assign:
                # Simple round-robin assignment
                target_shelf = available_shelves[hash(product_id) % len(available_shelves)]
            else:
                # Use first shelf as default
                target_shelf = available_shelves[0]

            # Update product shelf and status using update_row
            search_criteria = {"product_id": product_id}
            update_data = {
                "product_id": product_id,
                "rfid_tag": product.rfid_tag,
                "product_name": product.product_name,
                "status": ProductStatus.ON_SHELF,
                "supplier_id": product.supplier_id,
                "shelf_id": target_shelf.shelf_id,
                "price": product.price,
                "receipt_id": product.receipt_id
            }
            await self.db.update_row(Product, search_criteria, update_data)

            # Create shelf inventory record
            record_hash = hashlib.sha256(
                (str(now) + product_id + target_shelf.shelf_id).encode()
            ).hexdigest()[:10]
            record_id = f"SI_{record_hash}"

            shelf_inventory = ShelfInventory(
                shelf_inventory_id=record_id,
                shelf_id=target_shelf.shelf_id,
                product_id=product_id,
                added_timestamp=now
            )
            await self.db.insert(shelf_inventory)

            # Add to return dictionary
            if target_shelf.shelf_id not in shelf_inventory_records:
                shelf_inventory_records[target_shelf.shelf_id] = []
            shelf_inventory_records[target_shelf.shelf_id].append(shelf_inventory)

            print(f"Placed product {product_id} on shelf {target_shelf.shelf_id}")

        return shelf_inventory_records

    async def scan_shelf(self, shelf_id: str) -> Tuple[ShelfScan, List[Product]]:
        """Perform a scan of a shelf and record found products"""
        from Backend.src.Db.models import ShelfScan, ShelfScanItem

        # Create a scan record
        scan_hash = hashlib.sha256(str(datetime.datetime.now()).encode()).hexdigest()[:10]
        scan_id = f"SCAN_{scan_hash}"

        scan = ShelfScan(
            scan_id=scan_id,
            shelf_id=shelf_id,
            scan_timestamp=datetime.datetime.now()
        )
        await self.db.insert(scan)

        # Find all products that should be on this shelf
        expected_products = await self.db.search(Product, all_results=True, shelf_id=shelf_id,
                                                 status=ProductStatus.ON_SHELF)

        # Simulate scanning (in a real system, this would connect to RFID readers)
        found_products = []
        missing_products = []

        for product in expected_products:
            # For simulation: 95% chance products are found
            if random.random() < 0.95:
                found_products.append(product)

                # Create scan item record
                scan_item_hash = hashlib.sha256(
                    (scan_id + product.product_id).encode()
                ).hexdigest()[:10]
                scan_item_id = f"SCANITEM_{scan_item_hash}"

                scan_item = ShelfScanItem(
                    scan_item_id=scan_item_id,
                    scan_id=scan_id,
                    product_id=product.product_id
                )
                await self.db.insert(scan_item)
            else:
                missing_products.append(product)

        # Report missing products
        for product in missing_products:
            await self.report_missing_product(product.product_id)

        print(f"Shelf scan completed: Found {len(found_products)} products, Missing {len(missing_products)} products")
        return scan, found_products

    async def report_missing_product(self, product_id: str) -> None:
        """Mark a product as missing and update inventory theft count"""
        product = await self.db.search(Product, all_results=False, product_id=product_id)
        if not product:
            raise ValueError(f"Product {product_id} not found")

        # Get the inventory this product was in
        if product.shelf_id:
            shelf = await self.db.search(Shelf, all_results=False, shelf_id=product.shelf_id)
            if shelf:
                rack = await self.db.search(StorageRack, all_results=False, rack_id=shelf.rack_id)
                if rack:
                    # Update inventory theft count
                    inventory = await self.db.search(Inventory, all_results=False, inventory_id=rack.inventory_id)
                    if inventory:
                        # Update inventory theft count using update_row
                        search_criteria = {"inventory_id": inventory.inventory_id}
                        update_data = {
                            "inventory_id": inventory.inventory_id,
                            "owner_id": inventory.owner_id,
                            "location": inventory.location,
                            "previous_theft_count": inventory.previous_theft_count + 1
                        }
                        await self.db.update_row(Inventory, search_criteria, update_data)

        # Update product status using update_row
        search_criteria = {"product_id": product_id}
        update_data = {
            "product_id": product_id,
            "rfid_tag": product.rfid_tag,
            "product_name": product.product_name,
            "status": ProductStatus.MISSING,
            "supplier_id": product.supplier_id,
            "shelf_id": product.shelf_id,
            "price": product.price,
            "receipt_id": product.receipt_id
        }
        await self.db.update_row(Product, search_criteria, update_data)

        # If product was on a shelf, update ShelfInventory
        shelf_inventory = await self.db.search(
            ShelfInventory,
            all_results=False,
            product_id=product_id,
            removed_timestamp=None
        )

        if shelf_inventory:
            # Update shelf inventory using update_row
            search_criteria = {"shelf_inventory_id": shelf_inventory.shelf_inventory_id}
            update_data = {
                "shelf_inventory_id": shelf_inventory.shelf_inventory_id,
                "shelf_id": shelf_inventory.shelf_id,
                "product_id": shelf_inventory.product_id,
                "added_timestamp": shelf_inventory.added_timestamp,
                "removed_timestamp": datetime.datetime.now()
            }
            await self.db.update_row(ShelfInventory, search_criteria, update_data)

        print(f"Product {product_id} marked as missing")

    async def record_product_sale(self, product_id: str, inventory_id: str) -> Sale:
        """Record a product sale and update its status"""
        product = await self.db.search(Product, all_results=False, product_id=product_id)
        if not product:
            raise ValueError(f"Product {product_id} not found")

        # Create sale record
        sale_hash = hashlib.sha256(
            (str(datetime.datetime.now()) + product_id).encode()
        ).hexdigest()[:10]
        sale_id = f"SALE_{sale_hash}"

        sale = Sale(
            sale_id=sale_id,
            product_id=product_id,
            inventory_id=inventory_id,
            sale_timestamp=datetime.datetime.now()
        )

        # Update product status using update_row
        search_criteria = {"product_id": product_id}
        update_data = {
            "product_id": product_id,
            "rfid_tag": product.rfid_tag,
            "product_name": product.product_name,
            "status": ProductStatus.SOLD,
            "supplier_id": product.supplier_id,
            "shelf_id": None,  # Remove from shelf
            "price": product.price,
            "receipt_id": product.receipt_id
        }
        await self.db.update_row(Product, search_criteria, update_data)

        # If product was on a shelf, update ShelfInventory
        shelf_inventory = await self.db.search(
            ShelfInventory,
            all_results=False,
            product_id=product_id,
            removed_timestamp=None  # Only get active shelf inventory
        )

        if shelf_inventory:
            # Update shelf inventory using update_row
            search_criteria = {"shelf_inventory_id": shelf_inventory.shelf_inventory_id}
            update_data = {
                "shelf_inventory_id": shelf_inventory.shelf_inventory_id,
                "shelf_id": shelf_inventory.shelf_id,
                "product_id": shelf_inventory.product_id,
                "added_timestamp": shelf_inventory.added_timestamp,
                "removed_timestamp": datetime.datetime.now()
            }
            await self.db.update_row(ShelfInventory, search_criteria, update_data)

        # Insert sale
        await self.db.insert(sale)
        print(f"Recorded sale of product {product_id} from inventory {inventory_id}")

        return sale

    async def get_inventory_statistics(self, inventory_id: str) -> Dict[str, Any]:
        """Get comprehensive statistics about an inventory"""
        inventory = await self.db.search(Inventory, all_results=False, inventory_id=inventory_id)
        if not inventory:
            raise ValueError(f"Inventory {inventory_id} not found")

        # Get all racks in this inventory
        racks = await self.db.search(StorageRack, all_results=True, inventory_id=inventory_id)
        rack_ids = [rack.rack_id for rack in racks]

        # Get all shelves in these racks
        all_shelves = []
        for rack_id in rack_ids:
            shelves = await self.db.search(Shelf, all_results=True, rack_id=rack_id)
            all_shelves.extend(shelves)

        shelf_ids = [shelf.shelf_id for shelf in all_shelves]

        # Count products by status
        products_on_shelf = []
        for shelf_id in shelf_ids:
            products = await self.db.search(
                Product,
                all_results=True,
                shelf_id=shelf_id,
                status=ProductStatus.ON_SHELF
            )
            products_on_shelf.extend(products)

        # Get all sales for this inventory
        sales = await self.db.search(Sale, all_results=True, inventory_id=inventory_id)

        # Get all inventory receipts
        inventory_receipts = await self.db.search(
            InventoryReceipt,
            all_results=True,
            inventory_id=inventory_id
        )

        # Calculate total value
        total_shelf_value = sum(product.price for product in products_on_shelf)
        total_sales_value = 0
        for sale in sales:
            product = await self.db.search(Product, all_results=False, product_id=sale.product_id)
            if product:
                total_sales_value += product.price

        # Missing items calculation
        missing_products = []
        for shelf_id in shelf_ids:
            products = await self.db.search(
                Product,
                all_results=True,
                shelf_id=shelf_id,
                status=ProductStatus.MISSING
            )
            missing_products.extend(products)

        statistics = {
            "inventory_id": inventory_id,
            "location": inventory.location,
            "total_racks": len(racks),
            "total_shelves": len(all_shelves),
            "products_on_shelf": len(products_on_shelf),
            "total_shelf_value": total_shelf_value,
            "total_sales": len(sales),
            "total_sales_value": total_sales_value,
            "total_receipts": len(inventory_receipts),
            "missing_products": len(missing_products),
            "theft_count": inventory.previous_theft_count,
            "estimated_loss_value": sum(product.price for product in missing_products)
        }

        return statistics

    async def restock_inventory(self, inventory_id: str, supplier_id: str, min_threshold: int = 10) -> Optional[str]:
        """Automatically restock inventory if stock falls below threshold"""
        # Check current stock
        inventory = await self.db.search(Inventory, all_results=False, inventory_id=inventory_id)
        if not inventory:
            raise ValueError(f"Inventory {inventory_id} not found")

        # Get all racks in this inventory
        racks = await self.db.search(StorageRack, all_results=True, inventory_id=inventory_id)
        rack_ids = [rack.rack_id for rack in racks]

        # Get all shelves in these racks
        all_shelves = []
        for rack_id in rack_ids:
            shelves = await self.db.search(Shelf, all_results=True, rack_id=rack_id)
            all_shelves.extend(shelves)

        shelf_ids = [shelf.shelf_id for shelf in all_shelves]

        # Count products on shelves
        products_on_shelf = []
        for shelf_id in shelf_ids:
            products = await self.db.search(
                Product,
                all_results=True,
                shelf_id=shelf_id,
                status=ProductStatus.ON_SHELF
            )
            products_on_shelf.extend(products)

        # If below threshold, trigger restock
        if len(products_on_shelf) < min_threshold:
            print(
                f"Inventory {inventory_id} below threshold ({len(products_on_shelf)}/{min_threshold}). Triggering restock.")

            # This would typically call into SupplierManager to order more products
            # For demonstration purposes, let's simulate that here

            # Call an external SupplierManager to create new products (assuming it exists)
            # This is a placeholder - in a real system you'd import and use SupplierManager
            from Backend.src.manager.supplier_manager import SupplierManager
            supplier_manager = SupplierManager(self.session)

            # Order new products (20 is arbitrary for demo)
            products, receipt_id = await supplier_manager.create_random_products(
                supplier_id=supplier_id,
                supplier_name="Auto Restock Supplier",
                inventory_id=inventory_id,
                count=20
            )

            print(f"Restock order placed: Receipt ID {receipt_id}, {len(products)} products ordered")
            return receipt_id

        print(f"Inventory {inventory_id} has sufficient stock: {len(products_on_shelf)}/{min_threshold}")
        return None