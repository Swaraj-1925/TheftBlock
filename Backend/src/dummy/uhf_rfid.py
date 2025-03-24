import datetime
import hashlib
import random
from typing import List, Optional

from sqlmodel.ext.asyncio.session import AsyncSession
from ..dummy.base_sensor import BaseSensor
from ..Db.database_management import DatabaseManagement
from ..Db.models import Product, ShelfInventory, Sale, Shelf, StorageRack
from sqlmodel import select

class UHF_RFID(BaseSensor):
    def __init__(self, rfid_tag):
        super().__init__(rfid_tag)
        self.range = 2  # Range of Sensor

    def set_range(self, meters: Optional[int] = None):
        if meters is not None and meters <= 2:  # Fixed condition
            self.range = meters
            print(f"Range set to {self.range} meters")

    async def scan_item(self, session: AsyncSession) -> Optional[Product]:  # Adjusted return type
        stmt = select(Product).where(Product.rfid_tag == self.sensor_id)
        result = await session.exec(stmt)
        product = result.first()
        if product:
            print(f"Scanned product: {product}")
        else:
            print(f"No product found with RFID {self.sensor_id}")
        return product

    async def mark_as_sold(self, session: AsyncSession):
        # Step 1: Get the product
        stmt = select(Product).where(Product.rfid_tag == self.sensor_id)
        result = await session.exec(stmt)
        product = result.first()
        if not product:
            print(f"No product found with RFID {self.sensor_id} to mark as sold.")
            return

        # Step 2: Retrieve inventory_id
        inventory_id = None
        if product.shelf_id:
            shelf_stmt = select(Shelf).where(Shelf.shelf_id == product.shelf_id)
            shelf_result = await session.exec(shelf_stmt)
            shelf = shelf_result.first()
            if shelf:
                rack_stmt = select(StorageRack).where(StorageRack.rack_id == shelf.rack_id)
                rack_result = await session.exec(rack_stmt)
                rack = rack_result.first()
                if rack:
                    inventory_id = rack.inventory_id
                else:
                    print(f"No rack found for shelf {shelf.shelf_id}")
            else:
                print(f"No shelf found for shelf_id {product.shelf_id}")
        else:
            print(f"Product {product.product_id} has no shelf_id")

        # Step 3: Check if inventory_id was found
        if inventory_id is None:
            print(f"Cannot determine inventory_id for product {product.product_id}. Skipping sale record.")
            return

        # Step 4: Generate a unique sale_id
        sale_hash = hashlib.sha256(
            (str(datetime.datetime.now()) + product.product_id).encode()
        ).hexdigest()[:10]
        sale_id = f"SALE_{sale_hash}"

        # Step 5: Create Sale object with inventory_id
        sale = Sale(
            sale_id=sale_id,
            product_id=product.product_id,
            inventory_id=inventory_id,
            sale_timestamp=datetime.datetime.now()
        )
        session.add(sale)

        # Step 6: Update product status
        product.status = "sold"  # Adjust if ProductStatus enum is used
        session.add(product)

        # Step 7: Update ShelfInventory
        shelf_inv_stmt = select(ShelfInventory).where(
            ShelfInventory.product_id == product.product_id,
            ShelfInventory.removed_timestamp.is_(None)
        )
        shelf_inv_result = await session.exec(shelf_inv_stmt)
        shelf_item = shelf_inv_result.first()
        if shelf_item:
            shelf_item.removed_timestamp = datetime.datetime.now()
            session.add(shelf_item)

        # Step 8: Commit all changes
        await session.commit()
        print(f"Item {self.sensor_id} marked as sold by sensor {self.sensor_id}")

    async def is_sold(self, session: AsyncSession) -> bool:
        product = await self.scan_item(session=session)
        return product.status == "sold" if product else False

    async def scan_shelf(self, session: AsyncSession, shelf_id: str) -> List[str]:
        db = DatabaseManagement(session)
        stmt = select(ShelfInventory).where(
            ShelfInventory.shelf_id == shelf_id,
            ShelfInventory.removed_timestamp.is_(None)  # Only unsold products
        )
        result = await session.exec(stmt)
        shelf_items = result.all()

        detected_rfids = []
        for item in shelf_items:
            product = await db.search(Product, all_results=False, product_id=item.product_id)
            if product and product.status == "available":
                # Simulate RFID detection with a chance of "missing" (theft or scan failure)
                if random.random() > 0.2:  # 80% chance of detection
                    detected_rfids.append(product.rfid_tag)
                    print(f"Detected on shelf {shelf_id}: {product.product_id}, RFID: {product.rfid_tag}")
                else:
                    print(f"Simulated missing: {product.product_id}, RFID: {product.rfid_tag}")

        return detected_rfids

    async def read_sensor(self, session: AsyncSession) -> dict:
        product = await self.scan_item(session=session)
        status = product.status if product else None
        print(f"Reading sensor {self.sensor_id}: Status = {status}, Range = {self.range} meters")
        return {"id": self.sensor_id, "status": status, "range": self.range}