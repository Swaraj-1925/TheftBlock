"use client"

import { useState, useEffect } from "react"
import MetricCard from "./MetricCard"
import InventoryTable from "./InventoryTable"
import { fetchInventoryData, fetchInventoryStatistics } from "../api/inventory.jsx"

const Dashboard = ({ inventoryId, refreshTrigger, onSelectProduct }) => {
    const [inventoryData, setInventoryData] = useState({
        totalProducts: 0,
        onShelf: 0,
        theftCount: 0,
        items: [],
    })
    const [statistics, setStatistics] = useState(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    useEffect(() => {
        const getInventoryData = async () => {
            try {
                setLoading(true)
                console.log("Dashboard: Fetching inventory data for ID:", inventoryId)
                const data = await fetchInventoryData(inventoryId)
                console.log("Dashboard: Received inventory data:", data)
                setInventoryData(data)

                // Also fetch statistics
                console.log("Dashboard: Fetching inventory statistics for ID:", inventoryId)
                const stats = await fetchInventoryStatistics(inventoryId)
                console.log("Dashboard: Received inventory statistics:", stats)
                setStatistics(stats)

                setError(null)
            } catch (err) {
                console.error("Error fetching inventory data:", err)
                setError(`Failed to load inventory data: ${err.message}`)
            } finally {
                setLoading(false)
            }
        }

        getInventoryData()
    }, [inventoryId, refreshTrigger])

    // Listen for inventory updates
    useEffect(() => {
        const handleInventoryUpdated = () => {
            // Refresh data when inventory is updated
            const getInventoryData = async () => {
                try {
                    console.log("Dashboard: Refreshing inventory data after update")
                    const data = await fetchInventoryData(inventoryId)
                    setInventoryData(data)
                    const stats = await fetchInventoryStatistics(inventoryId)
                    setStatistics(stats)
                } catch (err) {
                    console.error("Error refreshing inventory data:", err)
                }
            }

            getInventoryData()
        }

        window.addEventListener("inventory-updated", handleInventoryUpdated)

        return () => {
            window.removeEventListener("inventory-updated", handleInventoryUpdated)
        }
    }, [inventoryId])

    return (
        <div className="bg-white rounded-lg shadow-md p-6">
            {error && <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">{error}</div>}

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <MetricCard title="Total Product" value={loading ? "..." : inventoryData.totalProducts.toLocaleString()} />
                <MetricCard title="On Shelf" value={loading ? "..." : inventoryData.onShelf.toLocaleString()} />
                <MetricCard title="Theft Count" value={loading ? "..." : inventoryData.theftCount.toLocaleString()} />
            </div>

            {statistics && (
                <div className="mb-8">
                    <h3 className="text-lg font-semibold mb-3">Additional Statistics</h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="bg-gray-50 p-3 rounded">
                            <p className="text-sm text-gray-500">Total Sales</p>
                            <p className="font-medium">{statistics.total_sales || 0}</p>
                        </div>
                        <div className="bg-gray-50 p-3 rounded">
                            <p className="text-sm text-gray-500">Sales Value</p>
                            <p className="font-medium">${(statistics.total_sales_value || 0).toLocaleString()}</p>
                        </div>
                        <div className="bg-gray-50 p-3 rounded">
                            <p className="text-sm text-gray-500">Estimated Loss</p>
                            <p className="font-medium">${(statistics.estimated_loss_value || 0).toLocaleString()}</p>
                        </div>
                    </div>
                </div>
            )}

            <InventoryTable items={inventoryData.items} loading={loading} onSelectProduct={onSelectProduct} />
        </div>
    )
}

export default Dashboard

