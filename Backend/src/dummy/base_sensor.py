import hashlib
import datetime
from itertools import product

from sqlmodel.ext.asyncio.session import AsyncSession

from Backend.src.Db.database_management import DatabaseManagement
from Backend.src.Db.models import Product

class BaseSensor:
    def __init__(self,rfid_tag: str):
        self.sensor_id = rfid_tag

    async def init_sensor(self,session: AsyncSession):
        timestamp = str(datetime.datetime.now())
        sensor_id_hash = hashlib.sha256(timestamp.encode()).hexdigest()[:10]
        self.sensor_id = f"SENSOR_{sensor_id_hash}"
        product_id =f"PRODUCT_{sensor_id_hash}"
        supplier_id = f"SUPPLIER_{sensor_id_hash}"

        sensor_data = Product(product_id=product_id,rfid_tag=self.sensor_id,product_name="Product")
        try:
            db = DatabaseManagement(session)
            await db.insert(sensor_data)
            print(f"Sensor created with ID: {self.sensor_id}")
        except Exception as e:
            print(e)
            print("ID collision detected, regenerating...")
            await self.init_sensor(session)
        return self.sensor_id

    async def get_sensor_id(self) -> str:
        if self.sensor_id:
            return self.sensor_id
        raise ValueError("Sensor not created yet. Call create_sensor() first.")

    def read_sensor(self,session: AsyncSession):
        """Base method to read sensor (to be overridden)."""
        raise NotImplementedError("Subclasses must implement read_sensor")


