from sqlmodel import SQLModel,Field
from datetime import datetime

class SensorModel(SQLModel, table=True):
    sensor_id: str = Field(primary_key=True)
    status: str = Field(default="unsold")
