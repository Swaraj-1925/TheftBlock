import datetime
import hashlib
import json
import random
from typing import Optional

from sqlmodel.ext.asyncio.session import AsyncSession
from Backend.src.Db.database_management import DatabaseManagement
from Backend.src.Db.models import Product, ShelfInventory, SupplierReceiptItem, SupplierReceipt, InventoryReceiptItem, \
    Shelf, InventoryReceipt


class WarehouseManager:
    def __init__(self, session: AsyncSession,shelf_ids:Optional[str]=None):
        self.session = session
        if shelf_ids is not None:
            self.shelf_ids = shelf_ids
        else:
            self.shelf_ids = [f"shelf_{i + 1}" for i in range(8)]
        self.db = DatabaseManagement(session)

    async def add_product(self, supplier_receipt_id: str)-> str:
        supplier_receipt = await self.db.search(SupplierReceipt, all_results=False, receipt_id=supplier_receipt_id)
        if not supplier_receipt:
            raise ValueError(f"Supplier receipt {supplier_receipt_id} not found!")
        receipt_hash = hashlib.sha256(str(datetime.datetime.now()).encode()).hexdigest()[:10]
        inventory_receipt_id = f"IR_{receipt_hash}"
        received_products = []
        supplier_items = await self.db.search(SupplierReceiptItem, all_results=True, receipt_id=supplier_receipt_id)

        #For testing Purpose
        for item in supplier_items:
            if random.random() > 0.3:  # 70% chance of receiving
                product = await self.db.search(Product, all_results=False, product_id=item.product_id)
                if product:
                    received_products.append(product)
                    print(f"Received product: {product.product_id}, RFID: {product.rfid_tag}")
            else:
                print(f"***Simulated loss: {item.product_id} not received!***")
        # for item in supplier_items:
        #     product = await self.db.search(Product, all_results=False, product_id=item.product_id)
        #     if product:
        #         received_products.append(product)
        #         print(f"Received product: {product.product_id}, RFID: {product.rfid_tag}")
        #     else:
        #         print(f"Simulated loss: {item.product_id} not received!")

        inventory_receipt = InventoryReceipt(
            receipt_id=inventory_receipt_id,
            supplier_receipt_id=supplier_receipt_id,
            date_received=datetime.datetime.now(),
            total_products_received=len(received_products)
        )
        await self.db.insert(inventory_receipt)
        print(f"Created inventory receipt: {inventory_receipt_id}")

        # Add received products to inventory receipt items and shelf inventory
        shelf = await self.db.search(Shelf, all_results=False, shelf_id="SHELF_001")
        if not shelf:
            shelf = Shelf(shelf_id="SHELF_001", shelf_location="Aisle 1, Shelf 1")
            await self.db.insert(shelf)

        for product in received_products:
            receipt_item_id = f"IRI_{hashlib.sha256(product.product_id.encode()).hexdigest()[:10]}"
            inventory_item = InventoryReceiptItem(
                receipt_item_id=receipt_item_id,
                receipt_id=inventory_receipt_id,
                product_id=product.product_id
            )
            await self.db.insert(inventory_item)

            shelf_inventory_id = f"SI_{hashlib.sha256(product.rfid_tag.encode()).hexdigest()[:10]}"
            shelf_inventory = ShelfInventory(
                shelf_inventory_id=shelf_inventory_id,
                shelf_id="SHELF_001",
                product_id=product.product_id,
                added_timestamp=datetime.datetime.now()
            )
            await self.db.insert(shelf_inventory)
            print(f"Added to shelf inventory: {product.product_id}, RFID: {product.rfid_tag}")

        return inventory_receipt_id

    async def verify_warehouse_receipt(self, receipt_filename: str) -> dict:
        if not receipt_filename.endswith(".json"):
            raise ValueError("Invalid receipt filename.")
        with open(receipt_filename, "r") as f:
            supplier_receipt = json.load(f)

        supplier_products = supplier_receipt["products"]
        total_supplied = supplier_receipt["total_products"]
        received_products = []
