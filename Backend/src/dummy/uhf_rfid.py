import datetime
import hashlib
import random
from typing import List

from typing_extensions import Optional

from sqlmodel.ext.asyncio.session import AsyncSession
from Backend.src.Db.database_management import DatabaseManagement
from Backend.src.dummy.base_sensor import BaseSensor
from Backend.src.Db.models import Product, ShelfInventory, Sale

from sqlmodel import select
class UHF_RFID(BaseSensor):
    def __init__(self,rfid_tag):
        super().__init__(rfid_tag)
        self.range = 2 #Range of Sensor

    def set_range(self, meters:Optional[int]=None):
        if meters is None and meters <= 2:
            self.range = meters
            print(f"Range set to {self.range} meters")


    async def scan_item(self,session: AsyncSession)->Optional[str]:
        stmt = select(Product).where(Product.rfid_tag == self.sensor_id)
        result = await session.exec(stmt)
        product = result.first()
        if product:
            print(f"Scanned product: {product}")
        else:
            print(f"No product found with RFID {self.sensor_id}")
        return product

    async def mark_as_sold(self,session: AsyncSession):
        stmt = select(Product).where(Product.rfid_tag == self.sensor_id)
        result = await session.exec(stmt)
        product = result.first()
        if product:
            product.status = "sold"
            session.add(product)
            # Add to Sale table
            sale_id = f"SALE_{hashlib.sha256(self.sensor_id.encode()).hexdigest()[:10]}"
            sale = Sale(
                sale_id=sale_id,
                product_id=product.product_id,
                sale_timestamp=datetime.datetime.now()
            )
            session.add(sale)

            # Update ShelfInventory
            stmt = select(ShelfInventory).where(
                ShelfInventory.product_id == product.product_id,
                ShelfInventory.removed_timestamp.is_(None)
            )
            result = await session.exec(stmt)
            shelf_item = result.first()
            if shelf_item:
                shelf_item.removed_timestamp = datetime.datetime.now()
                session.add(shelf_item)

            # Commit all changes
            await session.commit()
            print(f"Item {self.sensor_id} marked as sold by sensor {self.sensor_id}")
        else:
            print(f"No product found with RFID {self.sensor_id} to mark as sold.")

    async def is_sold(self,session: AsyncSession) -> bool:
        return await self.scan_item(session=session) == "sold"

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

    async def read_sensor(self,session: AsyncSession) -> dict:
        status = await self.scan_item(session=session)
        print(f"Reading sensor {self.sensor_id}: Status = {status}, Range = {self.range} meters")
        return {"id": self.sensor_id, "status": status, "range": self.range}




