from src.Db.database_management import DatabaseManagement
from src.Db.models import Product, ProductStatus, Shelf
from src.dummy.uhf_rfid import UHF_RFID
from src.manager.supplier_manager import SupplierManager
from src.Db.db import get_session, async_engine, create_db_and_tables
from src.manager.theft_detection_manager import TheftDetectionManager
from src.manager.warehouse_manager import WarehouseManager
import logging
import asyncio
import uuid
import hashlib
import datetime
import random

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("smart_inventory.log")
    ]
)
logger = logging.getLogger("smart_inventory")




def generate_id(tag:str):
    unique_id = str(uuid.uuid4())
    timestamp = str(datetime.datetime.now())
    id_hash = hashlib.sha256((timestamp + unique_id).encode()).hexdigest()[:10]
    id_tag = f"{tag}_{id_hash}"
    return id_tag


async def main():
    logger.info("=== Starting Smart Inventory System Simulation ===\n")

    # Create database and tables
    logger.info("Initializing database...\n")
    await create_db_and_tables()
    logger.info("Database initialized successfully\n")

    async for session in get_session():
        try:
            # Step 1: Setup inventory
            logger.info("\n=== Setting up inventory ===\n")
            warehouse_mgr = WarehouseManager(session)
            inventory_id = generate_id("INV")
            inventory = await warehouse_mgr.setup_inventory(
                inventory_id=inventory_id,
                owner_id="OWNER_001",
                location="Main Warehouse"
            )
            logger.info(f"Created inventory: {inventory_id} at {inventory.location}")

            # Setup racks and shelves
            racks = await warehouse_mgr.setup_racks_and_shelves(inventory_id, rack_count=3, num_shelf=4)
            logger.info(f"Created {len(racks)} racks with 4 shelves each")

            # Step 2: Create suppliers and their products
            logger.info("\n=== Creating suppliers and products ===\n")
            supplier_mgr = SupplierManager(session)

            # Supplier 1
            supplier1_id = "SUPPLIER_001"
            supplier1_name = "Electronics Inc."
            supplier1 = await supplier_mgr.create_supplier(supplier1_id, supplier1_name)
            logger.info(f"Created supplier: {supplier1_name} with ID {supplier1_id}")

            # Supplier 2
            supplier2_id = "SUPPLIER_002"
            supplier2_name = "Gadget World"
            supplier2 = await supplier_mgr.create_supplier(supplier2_id, supplier2_name)
            logger.info(f"Created supplier: {supplier2_name} with ID {supplier2_id}")

            # Link suppliers to inventory
            await supplier_mgr.link_supplier_to_inventory(supplier1_id, inventory_id)
            await supplier_mgr.link_supplier_to_inventory(supplier2_id, inventory_id)
            logger.info("Linked suppliers to inventory\n")

            # Create products for suppliers
            supplier1_products, supplier1_receipt_id = await supplier_mgr.create_random_products(
                supplier_id=supplier1_id,
                supplier_name=supplier1_name,
                inventory_id=inventory_id,
                count=10
            )
            logger.info(
                f"Created {len(supplier1_products)} products for {supplier1_name}, receipt: {supplier1_receipt_id}")

            supplier2_products, supplier2_receipt_id = await supplier_mgr.create_random_products(
                supplier_id=supplier2_id,
                supplier_name=supplier2_name,
                inventory_id=inventory_id,
                count=8
            )
            logger.info(
                f"Created {len(supplier2_products)} products for {supplier2_name}, receipt: {supplier2_receipt_id}")

            # Step 3: Warehouse receives products with optional loss simulation
            logger.info("\n=== Warehouse receiving products from suppliers ===\n")
            inventory_receipt1_id = await warehouse_mgr.receive_products(
                supplier_receipt_id=supplier1_receipt_id,
                inventory_id=inventory_id,
                loss_simulation=True  # Simulate some losses during receiving
            )
            logger.info(f"Received products from {supplier1_name} with receipt: {inventory_receipt1_id}\n")

            inventory_receipt2_id = await warehouse_mgr.receive_products(
                supplier_receipt_id=supplier2_receipt_id,
                inventory_id=inventory_id,
                loss_simulation=True
            )
            logger.info(f"Received products from {supplier2_name} with receipt: {inventory_receipt2_id}\n")

            # Step 4: Place products on shelves
            logger.info("\n=== Placing products on shelves ===\n")
            # Get all products with OUT_SHELF status
            db = DatabaseManagement(session)
            out_shelf_products = await db.search(Product, all_results=True, status=ProductStatus.OUT_SHELF)
            out_shelf_product_ids = [p.product_id for p in out_shelf_products]

            shelf_inventory = await warehouse_mgr.place_products_on_shelves(
                inventory_id=inventory_id,
                product_ids=out_shelf_product_ids,
                auto_assign=True
            )

            for shelf_id, items in shelf_inventory.items():
                logger.info(f"Placed {len(items)} products on shelf {shelf_id}\n")

            # Step 5: Initialize theft detection
            logger.info("\n=== Initializing theft detection ===\n")
            theft_detector = TheftDetectionManager(session)

            # Step 6: Perform shelf scans to detect missing items
            logger.info("\n=== Performing shelf scans ===\n")
            for shelf_id in list(shelf_inventory.keys()):
                logger.info(f"Scanning shelf: {shelf_id}")
                scan, found_products = await warehouse_mgr.scan_shelf(shelf_id)
                logger.info(f"Scan {scan.scan_id} completed: Found {len(found_products)} products\n")

                # Detect missing products from scan
                missing_products = await theft_detector.detect_missing_products(scan.scan_id)
                if missing_products:
                    logger.warning(f"Detected {len(missing_products)} missing products on shelf {shelf_id}\n")
                    for product in missing_products:
                        logger.warning(f"  - Missing: {product.product_name} (${product.price})\n")

            # Step 7: Simulate product sales
            logger.info("\n=== Simulating product sales ===")
            # Get a random sample of products to sell
            on_shelf_products = await db.search(Product, all_results=True, status=ProductStatus.ON_SHELF)
            products_to_sell = random.sample(on_shelf_products, min(3, len(on_shelf_products)))

            for product in products_to_sell:
                logger.info(f"Selling product: {product.product_name} (${product.price})\n")

                # Create RFID sensor for the product
                sensor = UHF_RFID(product.rfid_tag)
                logger.info(f"Created RFID sensor for product {product.product_id}\n")

                # Scan product before sale
                scan_result = await sensor.scan_item(session)
                logger.info(f"Pre-sale scan: {scan_result}\n")

                # Record sale
                sold = await sensor.mark_as_sold(session)
                if sold:
                    logger.info(f"Successfully sold product {product.product_id}\n")
                else:
                    logger.error(f"Failed to sell product {product.product_id}")

                # Verify product is sold
                is_sold = await sensor.is_sold(session)
                logger.info(f"Product sold status: {is_sold}")

            # Step 8: Simulate theft scenarios
            logger.info("\n=== Simulating theft scenarios ===")

            # Simulate a theft from a random shelf
            all_shelves = []
            for rack in racks:
                shelves = await db.search(Shelf, all_results=True, rack_id=rack.rack_id)
                all_shelves.extend(shelves)

            if all_shelves:
                target_shelf = random.choice(all_shelves)
                logger.info(f"Simulating theft from shelf {target_shelf.shelf_id}")

                # Get products on this shelf
                shelf_products = await db.search(Product, all_results=True,
                                                 shelf_id=target_shelf.shelf_id,
                                                 status=ProductStatus.ON_SHELF)

                # Choose a random product to "steal"
                if shelf_products:
                    stolen_product = random.choice(shelf_products)
                    theft_report = await theft_detector.report_theft(stolen_product.product_id)
                    logger.warning(f"Theft reported: {theft_report}")

            # Step 9: Generate inventory and theft statistics
            logger.info("\n=== Generating statistics ===")

            inventory_stats = await warehouse_mgr.get_inventory_statistics(inventory_id)
            logger.info("Inventory Statistics:")
            for key, value in inventory_stats.items():
                logger.info(f"  - {key}: {value}")

            theft_stats = await theft_detector.get_theft_statistics(inventory_id)
            logger.info("Theft Statistics:")
            for key, value in theft_stats.items():
                if not isinstance(value, dict):
                    logger.info(f"  - {key}: {value}")

            if theft_stats["high_risk_shelves"]:
                logger.warning(f"High-risk shelves detected: {theft_stats['high_risk_shelves']}")

            logger.info("\n=== Analyzing Theft Patterns ===")
            theft_patterns = await theft_detector.analyze_theft_patterns(inventory_id)
            logger.info("Theft Pattern Analysis:")
            for key, value in theft_patterns.items():
                if key not in ["insights", "theft_by_rack", "most_stolen_products", "high_value_missing_items"]:
                    logger.info(f"  - {key}: {value}")

            # Log insights
            if theft_patterns["insights"]:
                logger.info("Insights from theft analysis:")
                for insight in theft_patterns["insights"]:
                    logger.info(f"  - {insight}")

            # Log most stolen products
            if theft_patterns["most_stolen_products"]:
                logger.info("Most frequently stolen products:")
                for product in theft_patterns["most_stolen_products"]:
                    logger.info(f"  - {product['name']}: {product['count']} instances")

            # If there's high-value missing items, investigate relevant shelves
            if theft_patterns["high_value_missing_items"]:
                high_value_item = theft_patterns["high_value_missing_items"][0]
                shelf_id = high_value_item["shelf_id"]
                logger.info(f"\n=== Investigating High-Risk Shelf {shelf_id} ===")

                try:
                    shelf_investigation = await theft_detector.investigate_shelf(shelf_id)
                    logger.info(f"Shelf investigation for {shelf_id}:")
                    for key, value in shelf_investigation.items():
                        if key not in ["recommendations", "recent_scan_history"]:
                            logger.info(f"  - {key}: {value}")

                    # Log recommendations
                    if shelf_investigation["recommendations"]:
                        logger.info("Shelf security recommendations:")
                        for rec in shelf_investigation["recommendations"]:
                            logger.info(f"  - {rec}")
                except Exception as e:
                    logger.error(f"Error investigating shelf {shelf_id}: {str(e)}")

            # Generate theft prevention plan
            logger.info("\n=== Generating Theft Prevention Plan ===")
            try:
                prevention_plan = await theft_detector.generate_theft_prevention_plan(inventory_id)
                logger.info(f"Theft prevention plan for {inventory_id}:")
                logger.info(f"  - Current theft rate: {prevention_plan['current_theft_rate']}%")
                logger.info(f"  - Total value lost: ${prevention_plan['total_value_lost']}")

                # Log immediate actions
                logger.info("Immediate actions recommended:")
                for action in prevention_plan["immediate_actions"]:
                    logger.info(f"  - {action}")

                # Log medium term actions
                logger.info("Medium-term actions recommended:")
                for action in prevention_plan["medium_term_actions"]:
                    logger.info(f"  - {action}")

                # Log monitoring plan
                logger.info(f"Recommended scan frequency: {prevention_plan['monitoring_plan']['scan_frequency']}")
                logger.info(f"Recommended audit schedule: {prevention_plan['monitoring_plan']['audit_schedule']}")
            except Exception as e:
                logger.error(f"Error generating prevention plan: {str(e)}")

            logger.info("\n=== Smart Inventory Simulation Completed ===")

        except Exception as e:
            logger.error(f"Error in simulation: {str(e)}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())