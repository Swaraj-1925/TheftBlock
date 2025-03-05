from typing_extensions import Optional

from sqlmodel.ext.asyncio.session import AsyncSession
from Backend.src.Db.database_management import DatabaseManagement
from Backend.src.dummy.base_sensor import BaseSensor
from Backend.src.Db.models import Product

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
        product = await self.scan_item(session)
        if product:
            product.status = "sold"
            session.add(product)
            await session.commit()
            await session.refresh(product)
            print(f"Product {product.product_id} marked as sold by sensor {self.sensor_id}")
        else:
            print(f"No product found with RFID {self.sensor_id} to mark as sold.")

    async def is_sold(self,session: AsyncSession) -> bool:
        return await self.scan_item(session=session) == "sold"

    async def read_sensor(self,session: AsyncSession) -> dict:
        status = await self.scan_item(session=session)
        print(f"Reading sensor {self.sensor_id}: Status = {status}, Range = {self.range} meters")
        return {"id": self.sensor_id, "status": status, "range": self.range}




