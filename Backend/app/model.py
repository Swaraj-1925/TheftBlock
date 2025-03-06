from pydantic import BaseModel


class SupplierCreateRequest(BaseModel):
    supplier_id: str
    supplier_name: str
    product_count: int
