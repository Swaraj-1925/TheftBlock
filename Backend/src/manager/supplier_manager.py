import hashlib
import datetime
import random
import uuid
import asyncio
from typing import List, Tuple, Dict, Optional

from sqlmodel.ext.asyncio.session import AsyncSession
from ..Db.database_management import DatabaseManagement
from ..Db.models import Supplier, Product, SupplierReceipt, SupplierReceiptItem, ProductStatus, \
    InventorySupplier


class SupplierManager:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.db = DatabaseManagement(session)

    async def create_supplier(self, supplier_id: str, supplier_name: str) -> Dict:
        """Create a new supplier if it doesn't exist"""
        supplier = await self.db.search(Supplier, all_results=False, supplier_id=supplier_id)
        if not supplier:
            supplier = Supplier(supplier_id=supplier_id, supplier_name=supplier_name)
            await self.db.insert(supplier)
            print(f"Created supplier with ID: {supplier_id}")
        return supplier.model_dump()

    async def link_supplier_to_inventory(self, supplier_id: str, inventory_id: str) -> InventorySupplier:
        """Create a relationship between supplier and inventory"""
        # Check if relationship already exists
        existing_link = await self.db.search(
            InventorySupplier,
            all_results=False,
            supplier_id=supplier_id,
            inventory_id=inventory_id
        )

        if not existing_link:
            link_id = f"IS_{hashlib.sha256((supplier_id + inventory_id).encode()).hexdigest()[:10]}"
            inv_supplier = InventorySupplier(
                inventory_supplier_id=link_id,
                inventory_id=inventory_id,
                supplier_id=supplier_id
            )
            await self.db.insert(inv_supplier)
            print(f"Linked supplier {supplier_id} to inventory {inventory_id}")
            return inv_supplier

        return existing_link

    async def create_supplier_receipt(self, supplier_id: str, inventory_id: str, products: List[Product]) -> str:
        """Create a supplier receipt for products being sent to an inventory"""
        # Ensure the supplier is linked to the inventory
        await self.link_supplier_to_inventory(supplier_id, inventory_id)

        receipt_hash = hashlib.sha256(str(datetime.datetime.now()).encode()).hexdigest()[:10]
        receipt_id = f"SR_{receipt_hash}"

        receipt = SupplierReceipt(
            receipt_id=receipt_id,
            supplier_id=supplier_id,
            inventory_id=inventory_id,
            date_sent=datetime.datetime.now(),
            total_products_sent=len(products)
        )
        await self.db.insert(receipt)
        print(f"Created supplier receipt: {receipt_id}")

        # Create receipt items
        receipt_items = []
        for product in products:
            receipt_item_hash = hashlib.sha256(
                (str(datetime.datetime.now()) + product.product_id).encode()
            ).hexdigest()[:10]
            receipt_item_id = f"SRI_{receipt_item_hash}"
            receipt_item = SupplierReceiptItem(
                receipt_item_id=receipt_item_id,
                receipt_id=receipt_id,
                product_id=product.product_id
            )
            receipt_items.append(receipt_item)

            # Update product status and receipt ID using update_row
            search_criteria = {"product_id": product.product_id}
            update_data = {
                "product_id": product.product_id,
                "rfid_tag": product.rfid_tag,
                "product_name": product.product_name,
                "status": ProductStatus.WITH_SUPPLIER,
                "supplier_id": product.supplier_id,
                "shelf_id": product.shelf_id,
                "price": product.price,
                "receipt_id": receipt_id
            }
            await self.db.update_row(Product, search_criteria, update_data)

        try:
            async with self.session as session:
                for item in receipt_items:
                    await self.db.insert(item,auto_commit=False)
                await session.commit()  # Commit once after all inserts
        except Exception as e:
            await self.session.rollback()
            raise Exception(f"Failed to insert receipt items: {str(e)}")

        return receipt_id

    async def create_random_products(self, supplier_id: str, supplier_name: str, count: int,inventory_id: str=None ) -> \
    Tuple[
        List[Product], str]:
        """Create random products for a supplier and link them to an inventory"""
        # First create the supplier
        await self.create_supplier(supplier_id, supplier_name)

        products = [
            Product(
                product_id=f"PRODUCT_{uuid.uuid4().hex}",
                rfid_tag=f"RFID_{uuid.uuid4().hex}",
                product_name=random.choice(["Widget A", "Widget B", "Gadget X", "Tool Y"]),
                status=ProductStatus.WITH_SUPPLIER,  # Default status
                supplier_id=supplier_id,
                price=random.randint(50, 1000),
            )
            for _ in range(count)
        ]

        try:
            # Use a context manager to ensure proper session handling
            async with self.session as session:
                for product in products:
                    await self.db.insert(product,auto_commit=False)  # Insert one at a time
                await session.commit()  # Commit once after all inserts
        except Exception as e:
            await self.session.rollback()
            raise Exception(f"Failed to insert products: {str(e)}")

            # Create supplier receipt with these products
        receipt_id = "No inventory_id was provided"
        if inventory_id:
            receipt_id = await self.create_supplier_receipt(supplier_id, inventory_id, products)

        return products, receipt_id
