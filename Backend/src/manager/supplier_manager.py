import hashlib
import datetime
import random

from sqlmodel.ext.asyncio.session import AsyncSession
from Backend.src.Db.database_management import DatabaseManagement
from Backend.src.Db.models import Supplier, Product, SupplierReceipt, SupplierReceiptItem


class SupplierManager:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.db = DatabaseManagement(session)

    async def create_supplier(self, supplier_id: str, supplier_name: str) -> Supplier:
        supplier = await self.db.search(Supplier, all_results=False, supplier_id=supplier_id)
        if not supplier:
            supplier = Supplier(supplier_id=supplier_id, supplier_name=supplier_name)
            await self.db.insert(supplier)
            print(f"Created supplier with ID: {supplier_id}")
        return supplier

    async def create_random_products(self, supplier_id: str, supplier_name: str, count: int) -> tuple[
        list[Product], str]:
        await self.create_supplier(supplier_id, supplier_name)
        products = []

        # Generate receipt ID
        receipt_hash = hashlib.sha256(str(datetime.datetime.now()).encode()).hexdigest()[:10]
        receipt_id = f"SR_{receipt_hash}"

        # Create receipt
        receipt = SupplierReceipt(
            receipt_id=receipt_id,
            supplier_id=supplier_id,
            date_sent=datetime.datetime.now(),
            total_products_sent=count
        )
        await self.db.insert(receipt)
        print(f"Created supplier receipt: {receipt_id}")

        for i in range(count):
            product_hash = hashlib.sha256((str(datetime.datetime.now()) + str(i)).encode()).hexdigest()[:10]
            product_id = f"PRODUCT_{product_hash}"
            rfid_hash = hashlib.sha256((str(datetime.datetime.now()) + product_id).encode()).hexdigest()[:10]
            rfid_tag = f"RFID_{rfid_hash}"
            product_name = random.choice(["Widget A", "Widget B", "Gadget X", "Tool Y"])

            product = Product(
                product_id=product_id,
                rfid_tag=rfid_tag,
                product_name=product_name,
                supplier_id=supplier_id,
                status="available"
            )
            await self.db.insert(product)
            print(f"Created product with ID: {product_id}, RFID: {rfid_tag}, Supplier: {supplier_id}")

            # Add to receipt
            receipt_item_id = f"SRI_{product_hash}"
            receipt_item = SupplierReceiptItem(
                receipt_item_id=receipt_item_id,
                receipt_id=receipt_id,
                product_id=product_id
            )
            await self.db.insert(receipt_item)
            products.append(product)

        return products, receipt_id