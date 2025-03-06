from Backend.app.app import SupplierCreateRequest, app


@app.post("/api/supplier/create", response_model=dict)
async def create_supplier_and_products(
    supplier: SupplierCreateRequest,
    session: AsyncSession = Depends(get_session)
):
    supplier_manager = SupplierManager(session)
    products, receipt_id = await supplier_manager.create_random_products(
        supplier.supplier_id, supplier.supplier_name, supplier.product_count
    )
    return {
        "supplier_id": supplier.supplier_id,
        "receipt_id": receipt_id,
        "products_created": len(products)
    }