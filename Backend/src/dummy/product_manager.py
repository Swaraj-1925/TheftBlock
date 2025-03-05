import hashlib
import datetime
from sqlmodel.ext.asyncio.session import AsyncSession
from Backend.src.Db.database_management import DatabaseManagement
from Backend.src.Db.models import Supplier, Product

class ProductManager:
    async def create_supplier(self, supplier_id: str, supplier_name: str,session: AsyncSession) -> Supplier:
        db = DatabaseManagement(session)
        supplier = await db.search(Supplier, all_results=False, supplier_id=supplier_id)
        if not supplier:
            supplier = Supplier(supplier_id=supplier_id, supplier_name=supplier_name)
            await db.insert(supplier)
            print(f"Created supplier with ID: {supplier_id}")
        return supplier

    async def create_product(self, product_id: str, product_name: str, supplier_id: str,session: AsyncSession) -> Product:
        db = DatabaseManagement(session)


        existing_product = await db.search(Product, all_results=False, product_id=product_id)

        await self.create_supplier(supplier_id, f"Supplier_{supplier_id.split('_')[1]}",session=session)

        # Generate a unique RFID tag for the product
        timestamp = str(datetime.datetime.now())
        rfid_hash = hashlib.sha256((timestamp + product_id).encode()).hexdigest()[:10]
        rfid_tag = f"RFID_{rfid_hash}"

        product = Product(
            product_id=product_id,
            rfid_tag=rfid_tag,
            product_name=product_name,
            supplier_id=supplier_id
        )
        try:
            await db.insert(product)
            print(f"Created product with ID: {product_id}, RFID: {rfid_tag}, Supplier: {supplier_id}")
            return product
        except Exception as e:
            print(f"Error creating product: {e}")
            raise