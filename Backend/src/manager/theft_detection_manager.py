import asyncio
import datetime
import hashlib
import json
import random
from typing import Optional, List, Dict, Any, Tuple

from sqlmodel.ext.asyncio.session import AsyncSession
from Backend.src.Db.database_management import DatabaseManagement
from Backend.src.Db.models import (
    Product, ShelfInventory, ShelfScan, ShelfScanItem, Inventory,
    StorageRack, Shelf, ProductStatus, Sale, InventoryReceipt
)


class TheftDetectionManager:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.db = DatabaseManagement(session)

    async def detect_missing_products(self, scan_id: str) -> List[Product]:
        """
        Analyze a shelf scan to detect missing products that weren't found during scanning
        """
        # Get the scan record
        scan = await self.db.search(ShelfScan, all_results=False, scan_id=scan_id)
        if not scan:
            raise ValueError(f"Scan {scan_id} not found")

        # Get the shelf from the scan
        shelf = await self.db.search(Shelf, all_results=False, shelf_id=scan.shelf_id)
        if not shelf:
            raise ValueError(f"Shelf {scan.shelf_id} not found")

        # Get all products that should be on this shelf
        expected_products = await self.db.search(
            Product,
            all_results=True,
            shelf_id=scan.shelf_id,
            status=ProductStatus.ON_SHELF
        )

        # Get all products that were found in the scan
        scan_items = await self.db.search(ShelfScanItem, all_results=True, scan_id=scan_id)
        found_product_ids = {item.product_id for item in scan_items}

        # Products that were expected but not found
        missing_products = [p for p in expected_products if p.product_id not in found_product_ids]

        # Report all missing products
        for product in missing_products:
            await self.report_theft(product.product_id, scan_id)

        return missing_products

    async def report_theft(self, product_id: str, scan_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Report a product as stolen, updating inventory theft count and product status
        """
        product = await self.db.search(Product, all_results=False, product_id=product_id)
        if not product:
            raise ValueError(f"Product {product_id} not found")

        # Get the shelf and rack to determine inventory
        inventory_id = None
        if product.shelf_id:
            shelf = await self.db.search(Shelf, all_results=False, shelf_id=product.shelf_id)
            if shelf:
                rack = await self.db.search(StorageRack, all_results=False, rack_id=shelf.rack_id)
                if rack:
                    inventory_id = rack.inventory_id

        if not inventory_id:
            raise ValueError(f"Could not determine inventory for product {product_id}")

        # Update inventory theft count
        inventory = await self.db.search(Inventory, all_results=False, inventory_id=inventory_id)
        if inventory:
            # Update inventory theft count using update_row
            search_criteria = {"inventory_id": inventory.inventory_id}
            update_data = {
                "inventory_id": inventory.inventory_id,
                "owner_id": inventory.owner_id,
                "location": inventory.location,
                "previous_theft_count": inventory.previous_theft_count + 1
            }
            await self.db.update_row(Inventory, search_criteria, update_data)

        # Update product status to MISSING
        search_criteria = {"product_id": product_id}
        update_data = {
            "product_id": product_id,
            "rfid_tag": product.rfid_tag,
            "product_name": product.product_name,
            "status": ProductStatus.MISSING,
            "supplier_id": product.supplier_id,
            "shelf_id": product.shelf_id,
            "price": product.price,
            "receipt_id": product.receipt_id
        }
        await self.db.update_row(Product, search_criteria, update_data)

        # Update ShelfInventory
        shelf_inventory = await self.db.search(
            ShelfInventory,
            all_results=False,
            product_id=product_id,
            removed_timestamp=None
        )

        if shelf_inventory:
            # Update shelf inventory using update_row
            search_criteria = {"shelf_inventory_id": shelf_inventory.shelf_inventory_id}
            update_data = {
                "shelf_inventory_id": shelf_inventory.shelf_inventory_id,
                "shelf_id": shelf_inventory.shelf_id,
                "product_id": shelf_inventory.product_id,
                "added_timestamp": shelf_inventory.added_timestamp,
                "removed_timestamp": datetime.datetime.now()
            }
            await self.db.update_row(ShelfInventory, search_criteria, update_data)

        # Create a theft report dict
        theft_report = {
            "product_id": product_id,
            "product_name": product.product_name,
            "rfid_tag": product.rfid_tag,
            "shelf_id": product.shelf_id,
            "inventory_id": inventory_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "price": product.price,
            "scan_id": scan_id,
            "new_inventory_theft_count": inventory.previous_theft_count + 1
        }

        print(f"Theft detected: Product {product_id} ({product.product_name}) valued at ${product.price}")
        return theft_report

    async def get_theft_statistics(self, inventory_id: str) -> Dict[str, Any]:
        """
        Generate comprehensive theft statistics for an inventory
        """
        inventory = await self.db.search(Inventory, all_results=False, inventory_id=inventory_id)
        if not inventory:
            raise ValueError(f"Inventory {inventory_id} not found")

        # Get all racks in this inventory
        racks = await self.db.search(StorageRack, all_results=True, inventory_id=inventory_id)
        rack_ids = [rack.rack_id for rack in racks]

        # Get all shelves in these racks
        all_shelves = []
        for rack_id in rack_ids:
            shelves = await self.db.search(Shelf, all_results=True, rack_id=rack_id)
            all_shelves.extend(shelves)

        shelf_ids = [shelf.shelf_id for shelf in all_shelves]

        # Count missing products by each shelf
        missing_by_shelf = {}
        missing_products = []

        for shelf_id in shelf_ids:
            products = await self.db.search(
                Product,
                all_results=True,
                shelf_id=shelf_id,
                status=ProductStatus.MISSING
            )
            missing_by_shelf[shelf_id] = len(products)
            missing_products.extend(products)

        # Calculate total value lost
        total_value_lost = sum(product.price for product in missing_products)

        # Find shelves with highest loss rates
        sorted_shelves = sorted(missing_by_shelf.items(), key=lambda x: x[1], reverse=True)
        high_risk_shelves = [shelf_id for shelf_id, count in sorted_shelves[:3] if count > 0]

        # Get recent inventory receipts to analyze loss during receiving
        inventory_receipts = await self.db.search(
            InventoryReceipt,
            all_results=True,
            inventory_id=inventory_id
        )

        # Get total products received count across all receipts
        total_received = sum(receipt.total_products_received for receipt in inventory_receipts)

        # Calculate theft rate as percentage of inventory
        all_products = []
        for shelf_id in shelf_ids:
            products = await self.db.search(
                Product,
                all_results=True,
                shelf_id=shelf_id
            )
            all_products.extend(products)

        theft_rate = (len(missing_products) / max(1, len(all_products) + len(missing_products))) * 100

        statistics = {
            "inventory_id": inventory_id,
            "location": inventory.location,
            "total_theft_count": inventory.previous_theft_count,
            "missing_products_count": len(missing_products),
            "total_value_lost": total_value_lost,
            "theft_rate_percentage": round(theft_rate, 2),
            "high_risk_shelves": high_risk_shelves,
            "missing_by_shelf": missing_by_shelf,
            "average_value_per_theft": round(total_value_lost / max(1, len(missing_products)), 2),
            "total_products_received": total_received,
            "loss_during_receiving": inventory.previous_theft_count - len(
                missing_products) if inventory.previous_theft_count > len(missing_products) else 0
        }

        return statistics

    async def analyze_theft_patterns(self, inventory_id: str) -> Dict[str, Any]:
        """
        Analyze patterns in theft data to detect potential systemic issues
        """
        # Get basic theft statistics first
        theft_stats = await self.get_theft_statistics(inventory_id)

        # Get all racks in this inventory
        racks = await self.db.search(StorageRack, all_results=True, inventory_id=inventory_id)

        # Analyze theft by rack location
        theft_by_rack = {}
        for rack in racks:
            # Get all shelves in this rack
            shelves = await self.db.search(Shelf, all_results=True, rack_id=rack.rack_id)
            shelf_ids = [shelf.shelf_id for shelf in shelves]

            # Count missing products in this rack
            rack_missing_count = 0
            for shelf_id in shelf_ids:
                if shelf_id in theft_stats["missing_by_shelf"]:
                    rack_missing_count += theft_stats["missing_by_shelf"][shelf_id]

            theft_by_rack[rack.rack_id] = {
                "count": rack_missing_count,
                "location": rack.rack_location
            }

        # Find products with high value that are missing
        high_value_threshold = 500  # Arbitrary threshold
        high_value_missing = []

        # Get all missing products across the inventory
        missing_products = []
        for rack in racks:
            shelves = await self.db.search(Shelf, all_results=True, rack_id=rack.rack_id)
            for shelf in shelves:
                products = await self.db.search(
                    Product,
                    all_results=True,
                    shelf_id=shelf.shelf_id,
                    status=ProductStatus.MISSING
                )
                missing_products.extend(products)

        # Filter for high value items
        high_value_missing = [
            {
                "product_id": p.product_id,
                "name": p.product_name,
                "price": p.price,
                "shelf_id": p.shelf_id
            }
            for p in missing_products if p.price >= high_value_threshold
        ]

        # Determine if there's a pattern of theft of specific product types
        product_types = {}
        for product in missing_products:
            if product.product_name not in product_types:
                product_types[product.product_name] = 0
            product_types[product.product_name] += 1

        # Find the most commonly stolen product types
        sorted_product_types = sorted(product_types.items(), key=lambda x: x[1], reverse=True)

        # Check if sales and thefts correlate (higher sales might mean higher theft opportunities)
        sales = await self.db.search(Sale, all_results=True, inventory_id=inventory_id)

        analysis = {
            "inventory_id": inventory_id,
            "total_theft_count": theft_stats["total_theft_count"],
            "theft_by_rack": theft_by_rack,
            "high_value_missing_items": high_value_missing,
            "most_stolen_products": [{"name": name, "count": count} for name, count in sorted_product_types[:5]],
            "total_sales": len(sales),
            "theft_to_sales_ratio": round(theft_stats["missing_products_count"] / max(1, len(sales)), 4),
            "insights": []
        }

        # Generate insights based on the data
        if theft_stats["theft_rate_percentage"] > 10:
            analysis["insights"].append("High overall theft rate detected. Consider increased security measures.")

        if high_value_missing:
            analysis["insights"].append(
                f"High-value items are being targeted. Consider securing items valued over ${high_value_threshold}.")

        if sorted_product_types and sorted_product_types[0][1] > 5:
            analysis["insights"].append(f"Pattern detected: {sorted_product_types[0][0]} items are frequently stolen.")

        # Check if specific rack locations have disproportionate theft
        for rack_id, data in theft_by_rack.items():
            if data["count"] > theft_stats["missing_products_count"] * 0.5:  # If >50% of thefts from one rack
                analysis["insights"].append(
                    f"Rack {rack_id} ({data['location']}) accounts for most thefts. Consider repositioning or adding cameras.")

        return analysis

    async def investigate_shelf(self, shelf_id: str) -> Dict[str, Any]:
        """
        Conduct a thorough investigation of a specific shelf with theft issues
        """
        shelf = await self.db.search(Shelf, all_results=False, shelf_id=shelf_id)
        if not shelf:
            raise ValueError(f"Shelf {shelf_id} not found")

        # Get rack and inventory information
        rack = await self.db.search(StorageRack, all_results=False, rack_id=shelf.rack_id)
        if not rack:
            raise ValueError(f"Rack {shelf.rack_id} not found")

        inventory = await self.db.search(Inventory, all_results=False, inventory_id=rack.inventory_id)
        if not inventory:
            raise ValueError(f"Inventory {rack.inventory_id} not found")

        # Get all products currently on the shelf
        current_products = await self.db.search(
            Product,
            all_results=True,
            shelf_id=shelf_id,
            status=ProductStatus.ON_SHELF
        )

        # Get all missing products from this shelf
        missing_products = await self.db.search(
            Product,
            all_results=True,
            shelf_id=shelf_id,
            status=ProductStatus.MISSING
        )

        # Get shelf scan history
        shelf_scans = await self.db.search(ShelfScan, all_results=True, shelf_id=shelf_id)

        # Sort scans by timestamp
        shelf_scans.sort(key=lambda x: x.scan_timestamp, reverse=True)

        # Analyze scan history
        scan_history = []
        for scan in shelf_scans[:10]:  # Get the 10 most recent scans
            scan_items = await self.db.search(ShelfScanItem, all_results=True, scan_id=scan.scan_id)
            scan_history.append({
                "scan_id": scan.scan_id,
                "timestamp": scan.scan_timestamp.isoformat(),
                "items_found": len(scan_items)
            })

        # Get all shelf inventory records for this shelf
        shelf_inventory_records = await self.db.search(ShelfInventory, all_results=True, shelf_id=shelf_id)

        # Calculate how long products typically stay on this shelf
        product_durations = []
        for record in shelf_inventory_records:
            if record.added_timestamp and record.removed_timestamp:
                duration = (record.removed_timestamp - record.added_timestamp).total_seconds() / (60 * 60 * 24)  # Days
                product_durations.append(duration)

        avg_duration = sum(product_durations) / max(1, len(product_durations))

        # Calculate total value on shelf vs. missing value
        current_value = sum(p.price for p in current_products)
        missing_value = sum(p.price for p in missing_products)

        investigation = {
            "shelf_id": shelf_id,
            "shelf_location": shelf.shelf_location,
            "rack_id": rack.rack_id,
            "rack_location": rack.rack_location,
            "inventory_id": inventory.inventory_id,
            "current_products_count": len(current_products),
            "missing_products_count": len(missing_products),
            "current_value": current_value,
            "missing_value": missing_value,
            "theft_percentage": round(
                (missing_value / (current_value + missing_value)) * 100 if (current_value + missing_value) > 0 else 0,
                2),
            "avg_product_duration_days": round(avg_duration, 1),
            "recent_scan_history": scan_history,
            "recommendations": []
        }

        # Generate recommendations based on the investigation
        if len(missing_products) > 2:
            investigation["recommendations"].append("Install additional security camera covering this shelf")

        if missing_value > 1000:
            investigation["recommendations"].append("Consider placing high-value items in more secure locations")

        if investigation["theft_percentage"] > 20:
            investigation["recommendations"].append("Implement frequent random audits for this shelf")

        if avg_duration < 3 and len(product_durations) > 5:
            investigation["recommendations"].append(
                "High product turnover detected. Consider reorganizing product placement")

        return investigation

    async def predict_theft_risk(self, product_id: str) -> Dict[str, Any]:
        """
        Calculate the risk of theft for a specific product
        """
        product = await self.db.search(Product, all_results=False, product_id=product_id)
        if not product:
            raise ValueError(f"Product {product_id} not found")

        risk_factors = {
            "base_risk": 0.05,  # 5% base risk
            "price_factor": 0,
            "shelf_factor": 0,
            "product_type_factor": 0
        }

        # Higher price = higher risk
        if product.price > 500:
            risk_factors["price_factor"] = 0.2
        elif product.price > 200:
            risk_factors["price_factor"] = 0.1
        elif product.price > 100:
            risk_factors["price_factor"] = 0.05

        # Check if product is on a high-risk shelf
        if product.shelf_id:
            shelf = await self.db.search(Shelf, all_results=False, shelf_id=product.shelf_id)
            if shelf:
                rack = await self.db.search(StorageRack, all_results=False, rack_id=shelf.rack_id)
                if rack:
                    # Get inventory
                    inventory = await self.db.search(Inventory, all_results=False, inventory_id=rack.inventory_id)
                    if inventory and inventory.previous_theft_count > 10:
                        risk_factors["shelf_factor"] = 0.15

                    # Get all missing products from this shelf
                    missing_from_shelf = await self.db.search(
                        Product,
                        all_results=True,
                        shelf_id=product.shelf_id,
                        status=ProductStatus.MISSING
                    )

                    if len(missing_from_shelf) > 3:
                        risk_factors["shelf_factor"] = max(risk_factors["shelf_factor"], 0.25)

        # Check if similar products have been stolen
        # Get all missing products with the same name
        similar_missing = await self.db.search(
            Product,
            all_results=True,
            product_name=product.product_name,
            status=ProductStatus.MISSING
        )

        if len(similar_missing) > 2:
            risk_factors["product_type_factor"] = 0.2
        elif len(similar_missing) > 0:
            risk_factors["product_type_factor"] = 0.1

        # Calculate total risk percentage
        total_risk = sum(risk_factors.values())
        risk_percentage = min(total_risk * 100, 95)  # Cap at 95%

        risk_assessment = {
            "product_id": product_id,
            "product_name": product.product_name,
            "price": product.price,
            "risk_percentage": round(risk_percentage, 1),
            "risk_level": "High" if risk_percentage > 50 else "Medium" if risk_percentage > 25 else "Low",
            "risk_factors": risk_factors,
            "recommendations": []
        }

        # Add recommendations based on risk level
        if risk_percentage > 50:
            risk_assessment["recommendations"].extend([
                "Move to high-security area",
                "Use additional security tags",
                "Implement frequent auditing"
            ])
        elif risk_percentage > 25:
            risk_assessment["recommendations"].extend([
                "Consider repositioning on shelf",
                "Include in regular audit cycles"
            ])

        return risk_assessment

    async def generate_theft_prevention_plan(self, inventory_id: str) -> Dict[str, Any]:
        """
        Generate a comprehensive theft prevention plan for an inventory based on analysis
        """
        # First get theft statistics and analysis
        theft_stats = await self.get_theft_statistics(inventory_id)
        theft_patterns = await self.analyze_theft_patterns(inventory_id)

        # Identify high-risk areas and products
        high_risk_shelves = theft_stats["high_risk_shelves"]

        # Get inventory details
        inventory = await self.db.search(Inventory, all_results=False, inventory_id=inventory_id)
        if not inventory:
            raise ValueError(f"Inventory {inventory_id} not found")

        # Develop a prevention plan
        prevention_plan = {
            "inventory_id": inventory_id,
            "location": inventory.location,
            "current_theft_rate": theft_stats["theft_rate_percentage"],
            "total_value_lost": theft_stats["total_value_lost"],
            "immediate_actions": [],
            "medium_term_actions": [],
            "long_term_strategies": [],
            "high_risk_areas": [{
                "shelf_id": shelf_id,
                "recommended_security_level": "High"
            } for shelf_id in high_risk_shelves],
            "monitoring_plan": {
                "scan_frequency": "Daily" if theft_stats["theft_rate_percentage"] > 10 else "Weekly",
                "audit_schedule": "Bi-weekly" if theft_stats["theft_rate_percentage"] > 5 else "Monthly",
                "performance_metrics": [
                    "Theft rate reduction percentage",
                    "Value of prevented thefts",
                    "Recovery rate of missing items"
                ]
            }
        }

        # Add immediate actions based on severity
        if theft_stats["theft_rate_percentage"] > 15:
            prevention_plan["immediate_actions"].extend([
                "Conduct full inventory audit within 48 hours",
                "Install temporary surveillance in high-risk areas",
                "Implement mandatory bag checks for all personnel"
            ])
        elif theft_stats["theft_rate_percentage"] > 5:
            prevention_plan["immediate_actions"].extend([
                "Increase random shelf scans in high-risk areas",
                "Brief all staff on theft prevention protocols",
                "Review camera footage of high-risk shelves"
            ])
        else:
            prevention_plan["immediate_actions"].extend([
                "Continue regular monitoring",
                "Conduct focused audits on high-value products"
            ])

        # Medium-term actions
        prevention_plan["medium_term_actions"].extend([
            "Update product placement strategy to place high-value items in more secure locations",
            "Implement additional RFID readers at strategic points",
            f"Retrain staff on inventory management procedures focusing on {theft_patterns['most_stolen_products'][0]['name'] if theft_patterns['most_stolen_products'] else 'high-value items'}",
            "Establish regular security review meetings"
        ])

        # Long-term strategies
        prevention_plan["long_term_strategies"].extend([
            "Develop predictive theft analytics using historical data",
            "Implement advanced security measures for high-value products",
            "Optimize inventory layouts to reduce theft opportunities",
            "Establish partnerships with local law enforcement for theft prevention"
        ])

        return prevention_plan