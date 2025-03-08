from typing import Annotated, List, Any

from fastapi import APIRouter, Query, Depends, HTTPException,status
from sqlmodel.ext.asyncio.session import AsyncSession

from Backend.app.res_models import SupplierResponse, ProductResponse, ProductDetailsResponse
from Backend.app.services.supplier import make_supplier
from Backend.src.Db.db import get_session
from Backend.src.Db.models import Product
from Backend.src.manager.supplier_manager import SupplierManager

supplier_router = APIRouter(prefix="/supplier",tags=["Supplier"])

@supplier_router.post("/create",description="Create a supplier",response_model=SupplierResponse)
async def create_supplier(supplier_name:Annotated[str | None, Query()],session: AsyncSession = Depends(get_session)):
    """Create Supplier"""
    sup = await make_supplier(session=session,supplier_name=supplier_name)
    supplier = SupplierResponse(
        supplier_id=sup.supplier_id,
        supplier_name=sup.supplier_name
    )
    return supplier

@supplier_router.post("/create_receipt",description="Create a supplier receipt",response_model=str)
async def create_supplier_receipt(supplier_id:Annotated[str, Query()],
                                  inventory_id:Annotated[str, Query()],
                                  request: ProductDetailsResponse,
                                  session: AsyncSession = Depends(get_session)):
    """Create Supplier Receipt"""
    try:
        products = [
            Product(
                product_id=product,
                rfid_tag=product.rfid_tag,
                product_name=product.product_name,
                status=product.status,
                supplier_id=product.supplier_id,
                price=product.price,
            )
            for product in request.products
        ]
        suppler_manager = SupplierManager(session=session)
        receipt_id = suppler_manager.create_supplier_receipt(supplier_id=supplier_id,inventory_id=inventory_id,products=products)
        return receipt_id
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error Creating Products: {str(e)}"
        )