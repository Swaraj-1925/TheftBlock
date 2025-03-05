from typing_extensions import Optional

from sqlmodel.ext.asyncio.session import AsyncSession
from Backend.src.Db.database_management import DatabaseManagement
from Backend.src.Db.models.SensorModel import SensorModel
from Backend.src.dummy.base_sensor import BaseSensor


class UHF_RFID(BaseSensor):
    def __init__(self):
        super().__init__()
        self.range = 2 #Range of Sensor

    def set_range(self, meters:Optional[int]=None):
        if meters is None and meters <= 2:
            self.range = meters
            print(f"Range set to {self.range} meters")


    async def scan_item(self,session: AsyncSession)->Optional[str]:
        db = DatabaseManagement(session)
        result = await db.search(SensorModel,all_results=False,sensor_id=self.sensor_id)
        if result:
            return result
        else:
            return None
    async def mark_as_sold(self,session: AsyncSession):
        db = DatabaseManagement(session)
        update_data = {"sensor_id": self.sensor_id, "status": "sold"}
        await  db.update_row(
            model=SensorModel,
            search_criteria={"sensor_id": self.sensor_id},
            update_data=update_data,
            insert_if_not_exist=False
        )
        print(f"Item {self.sensor_id} marked as sold")

    async def is_sold(self,session: AsyncSession) -> bool:
        return await self.scan_item(session=session) == "sold"

    async def read_sensor(self,session: AsyncSession) -> dict:
        status = await self.scan_item(session=session)
        print(f"Reading sensor {self.sensor_id}: Status = {status}, Range = {self.range} meters")
        return {"id": self.sensor_id, "status": status, "range": self.range}




