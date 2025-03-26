"use client"

import { useState, useEffect } from "react"
import { Outlet } from "react-router-dom"
import Sidebar from "./Sidebar"
import { fetchInventories } from "../api/inventory"

function Layout() {
    const [activeInventory, setActiveInventory] = useState(null)
    const [inventories, setInventories] = useState([])
    const [refreshTrigger, setRefreshTrigger] = useState(0)

    // Fetch inventories on load and when refresh is triggered
    useEffect(() => {
        const getInventories = async () => {
            try {
                console.log("Fetching inventories...")
                const data = await fetchInventories()
                console.log("Received inventories:", data)
                setInventories(data)

                // Set the first inventory as active if none is selected
                if (!activeInventory && data.length > 0) {
                    console.log("Setting active inventory to:", data[0])
                    setActiveInventory(data[0])
                }
            } catch (error) {
                console.error("Error fetching inventories:", error)
                // Show error message to user
                alert(`Failed to fetch inventories: ${error.message}`)
            }
        }

        getInventories()
    }, [refreshTrigger, activeInventory])

    // Function to trigger a refresh of data
    const refreshData = () => {
        setRefreshTrigger((prev) => prev + 1)
    }

    // Listen for inventory updates
    useEffect(() => {
        const handleInventoryUpdated = () => {
            refreshData()
        }

        // Listen for theft added event
        const handleTheftAdded = () => {
            refreshData()
        }

        window.addEventListener("inventory-updated", handleInventoryUpdated)
        window.addEventListener("theft-added", handleTheftAdded)

        return () => {
            window.removeEventListener("inventory-updated", handleInventoryUpdated)
            window.removeEventListener("theft-added", handleTheftAdded)
        }
    }, [])

    return (
        <div className="flex h-screen bg-gray-100">
            <Sidebar
                inventories={inventories}
                activeInventory={activeInventory}
                setActiveInventory={setActiveInventory}
                onRefresh={refreshData}
            />
            <div className="flex-1 flex flex-col overflow-hidden">
                <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-100 p-6">
                    <div className="container mx-auto">
                        <h1 className="text-4xl font-semibold text-center text-blue-600 mb-8">WareHouse Management</h1>
                        <Outlet context={{ activeInventory, refreshTrigger, refreshData }} />
                    </div>
                </main>
            </div>
        </div>
    )
}

export default Layout

