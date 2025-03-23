from typing import Annotated, List, Dict

from fastapi import APIRouter, Query, Depends, HTTPException,status,Path
from sqlmodel.ext.asyncio.session import AsyncSession

from Backend.app.res_models import SupplierResponse, ProductResponse
from Backend.app.services.supplier import make_supplier
from Backend.src.Db.db import get_session
from Backend.src.manager.supplier_manager import SupplierManager

test_router = APIRouter(prefix="/test",tags=["Testing"])

@test_router.post("/create_products",description="Take an number as input and create that many number of products",response_model=List[ProductResponse])
async def create_products(num_products:Annotated[int,Query()],supplier_name:Annotated[str, Query()],supplier_id:Annotated[str, Query()],session:AsyncSession = Depends(get_session)):
    try:
        suppler_manager = SupplierManager(session=session)
        products, _ = await suppler_manager.create_random_products(
            supplier_name=supplier_name,
            supplier_id=supplier_id,
            count=num_products
        )
        return products
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error Creating Products: {str(e)}"
        )

@test_router.post("/{inventory_id}/create_products",description="Create a supplier receipt",response_model=Dict)
async def create_supplier_receipt(
        num_products:Annotated[int,Query()],
        supplier_name:Annotated[str, Query()],
        supplier_id:Annotated[str, Query()],
        inventory_id: Annotated[str, Path()],
        session:AsyncSession = Depends(get_session)):
    try:
        suppler_manager = SupplierManager(session=session)
        products, receipt_id = await suppler_manager.create_random_products(
            supplier_name=supplier_name,
            supplier_id=supplier_id,
            count=num_products,
            inventory_id=inventory_id
        )
        return {"Products":products,"receipt_id":receipt_id}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error Creating Products: {str(e)}"
        )