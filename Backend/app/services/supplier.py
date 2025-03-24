from fastapi import HTTPException,status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.res_models import SupplierResponse
from app.services.utils import generate_id
from src.manager.supplier_manager import SupplierManager


def make_supplier(session:AsyncSession,supplier_name:str)->SupplierResponse:
    try:
        supplier_manager = SupplierManager(session)
        supplier_id = generate_id("sup")
        supplier = supplier_manager.create_supplier(supplier_id=supplier_id,supplier_name=supplier_name)
        return supplier
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error Creating suppliers: {str(e)}"
        )