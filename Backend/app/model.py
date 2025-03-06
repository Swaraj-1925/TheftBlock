from pydantic import BaseModel


class SupplierCreate(BaseModel):
    supplier_id: str
    supplier_name: str
