import asyncio

from sqlmodel import select

from Backend.src.Db.database_management import DatabaseManagement
from sqlmodel.ext.asyncio.session import AsyncSession

from Backend.src.Db.models import SupplierReceipt, InventoryReceipt, InventoryReceiptItem, SupplierReceiptItem, Sale, \
    ShelfInventory, Product
from Backend.src.dummy.uhf_rfid import UHF_RFID


class TheftDetectionManager:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.db = DatabaseManagement(session)

    async def _fetch_supplier_to_warehouse_data(self, supplier_receipt_id: str) -> tuple[int, set, int, set]:
        """Fetch data for supplier-to-warehouse theft detection."""
        supplier_receipt = await self.db.search(SupplierReceipt, all_results=False, receipt_id=supplier_receipt_id)
        if not supplier_receipt:
            raise ValueError(f"Supplier receipt {supplier_receipt_id} not found!")

        inventory_receipt = await self.db.search(InventoryReceipt, all_results=False,
                                                 supplier_receipt_id=supplier_receipt_id)
        if not inventory_receipt:
            raise ValueError(f"No inventory receipt found for supplier receipt {supplier_receipt_id}")

        supplier_items = await self.db.search(SupplierReceiptItem, all_results=True, receipt_id=supplier_receipt_id)
        inventory_items = await self.db.search(InventoryReceiptItem, all_results=True,
                                               receipt_id=inventory_receipt.receipt_id)

        total_sent = supplier_receipt.total_products_sent
        sent_product_ids = {item.product_id for item in supplier_items}
        total_received = inventory_receipt.total_products_received
        received_product_ids = {item.product_id for item in inventory_items}

        return total_sent, sent_product_ids, total_received, received_product_ids

    async def _fetch_warehouse_to_consumer_data(self, shelf_id: str) -> tuple[int, set, int, set]:
        """Fetch data for warehouse-to-consumer theft detection."""
        shelf_inventory_items = await self.db.search(ShelfInventory, all_results=True, shelf_id=shelf_id,
                                                     removed_timestamp=None)
        sale_items = await self.db.search(Sale, all_results=True)

        total_sent = len(shelf_inventory_items)  # Products expected to be sold
        sent_product_ids = {item.product_id for item in shelf_inventory_items}
        sale_product_ids = {sale.product_id for sale in sale_items}
        received_product_ids = sent_product_ids.intersection(sale_product_ids)  # Products confirmed sold
        total_received = len(received_product_ids)

        return total_sent, sent_product_ids, total_received, received_product_ids

    def _analyze_theft(self, total_sent: int, sent_product_ids: set, total_received: int, received_product_ids: set,
                       stage_name: str) -> dict:
        """Analyze theft based on sent and received data."""
        missing_products = sent_product_ids - received_product_ids
        result = {
            "stage": stage_name,
            "total_sent": total_sent,
            "total_received": total_received,
            "discrepancy": total_sent - total_received,
            "theft_detected": total_received != total_sent,
            "missing_products": list(missing_products)
        }
        if result["theft_detected"]:
            print(
                f"{stage_name} theft detected! Sent: {total_sent}, Received: {total_received}, Missing: {result['missing_products']}")
        else:
            print(f"No {stage_name} theft detected. All {total_received} products accounted for.")
        return result

    async def detect_theft(self, stage: str, source_id: str) -> dict:
        if stage == "supplier_to_warehouse":
            total_sent, sent_product_ids, total_received, received_product_ids = await self._fetch_supplier_to_warehouse_data(
                source_id)
            stage_name = "Supplier to Warehouse"
        elif stage == "warehouse_to_consumer":
            total_sent, sent_product_ids, total_received, received_product_ids = await self._fetch_warehouse_to_consumer_data(
                source_id)
            stage_name = "Warehouse to Consumer"
        else:
            raise ValueError(f"Unsupported stage: {stage}. Use 'supplier_to_warehouse' or 'warehouse_to_consumer'.")

        return self._analyze_theft(total_sent, sent_product_ids, total_received, received_product_ids, stage_name)

    async def detect_shelf_theft(self, shelf_id: str, check_interval_seconds: int = 5, max_checks: int = 3):
        """Periodically check a shelf for missing available products using a simulated RFID reader."""
        print(f"\nStarting shelf theft detection for shelf {shelf_id} every {check_interval_seconds} seconds...")

        # Get expected available products from ShelfInventory
        stmt = select(ShelfInventory).where(
            ShelfInventory.shelf_id == shelf_id,
            ShelfInventory.removed_timestamp.is_(None)
        )
        result = await self.session.exec(stmt)
        shelf_items = result.all()

        expected_rfids = set()
        for item in shelf_items:
            product = await self.db.search(Product, all_results=False, product_id=item.product_id)
            if product and product.status == "available":
                expected_rfids.add(product.rfid_tag)

        if not expected_rfids:
            print(f"No available products on shelf {shelf_id} to check.")
            return

        # Simulate RFID reader for the shelf (using one sensor instance for simplicity)
        rfid_reader = UHF_RFID(next(iter(expected_rfids)))  # Use first RFID as reader ID

        for check in range(max_checks):
            print(f"\nShelf check #{check + 1}")
            detected_rfids = await rfid_reader.scan_shelf(self.session, shelf_id)
            detected_rfids_set = set(detected_rfids)
            missing_rfids = expected_rfids - detected_rfids_set

            if missing_rfids:
                missing_products = []
                for rfid in missing_rfids:
                    product = await self.db.search(Product, all_results=False, rfid_tag=rfid)
                    if product:
                        missing_products.append(product.product_id)
                print(f"Shelf theft detected on {shelf_id}! Missing products: {missing_products}")
            else:
                print(f"No shelf theft detected on {shelf_id}. All products present.")

            if check < max_checks - 1:  # Don’t sleep after the last check
                await asyncio.sleep(check_interval_seconds)

        print(f"Shelf theft detection completed for {shelf_id}.")