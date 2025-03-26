"use client"

import { useState, useEffect } from "react"
import { Package, Plus } from "lucide-react"
import AddInventoryForm from "./AddInventoryForm"
import { addInventoryItem, fetchInventoryData } from "../api/inventory"

const Sidebar = ({ inventories = [], activeInventory, setActiveInventory, onRefresh }) => {
    const [showAddForm, setShowAddForm] = useState(false)
    const [products, setProducts] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    // Fetch products for the active inventory
    useEffect(() => {
        const getProducts = async () => {
            if (activeInventory?.inventory_id) {
                try {
                    setLoading(true)
                    const data = await fetchInventoryData(activeInventory.inventory_id)
                    setProducts(data.items || [])
                    setError(null)
                } catch (error) {
                    console.error("Error fetching products:", error)
                    setError("Failed to load products")
                } finally {
                    setLoading(false)
                }
            }
        }

        getProducts()
    }, [activeInventory])

    // Listen for inventory updates
    useEffect(() => {
        const handleInventoryUpdated = () => {
            if (activeInventory?.inventory_id) {
                const getProducts = async () => {
                    try {
                        const data = await fetchInventoryData(activeInventory.inventory_id)
                        setProducts(data.items || [])
                        setError(null)
                    } catch (error) {
                        console.error("Error refreshing products:", error)
                        setError("Failed to refresh products")
                    }
                }

                getProducts()
                onRefresh()
            }
        }

        window.addEventListener("inventory-updated", handleInventoryUpdated)

        return () => {
            window.removeEventListener("inventory-updated", handleInventoryUpdated)
        }
    }, [activeInventory, onRefresh])

    const handleAddInventory = async (data) => {
        try {
            await addInventoryItem(data)
            // Close the form
            setShowAddForm(false)
            // Refresh the data
            onRefresh()
            // Show success message
            alert("Product added successfully!")
        } catch (error) {
            console.error("Error adding inventory item:", error)
            alert("Failed to add product. Please try again.")
        }
    }

    return (
        <div className="w-64 bg-white shadow-md z-10">
            <div className="p-6">
                <div className="flex items-center gap-2 mb-8">
                    <Package className="h-8 w-8 text-blue-500" />
                    <h2 className="text-2xl font-bold">Inventory</h2>
                </div>

                {/* Inventory selector */}
                <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-1">Select Warehouse</label>
                    <select
                        className="w-full px-3 py-2 border border-gray-300 rounded-md"
                        value={activeInventory?.inventory_id || ""}
                        onChange={(e) => {
                            const selected = inventories.find((inv) => inv.inventory_id === e.target.value)
                            if (selected) setActiveInventory(selected)
                        }}
                    >
                        {inventories.length === 0 ? (
                            <option value="">No warehouses found</option>
                        ) : (
                            inventories.map((inventory) => (
                                <option key={inventory.inventory_id} value={inventory.inventory_id}>
                                    {inventory.location || `Warehouse ${inventory.inventory_id}`}
                                </option>
                            ))
                        )}
                    </select>
                </div>

                {/* Products list */}
                <div className="mb-4">
                    <h3 className="text-sm font-medium text-gray-700 mb-2">Products in Warehouse</h3>
                    {error && <div className="text-red-500 text-sm mb-2">{error}</div>}
                    {loading ? (
                        <div className="text-center py-4 text-gray-500">Loading products...</div>
                    ) : products.length === 0 ? (
                        <div className="text-center py-4 text-gray-500">No products found</div>
                    ) : (
                        <div className="max-h-64 overflow-y-auto">
                            <ul className="space-y-1">
                                {products.map((product) => (
                                    <li key={product.id} className="text-sm py-1 px-2 rounded hover:bg-gray-100">
                                        {product.name}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}
                </div>
            </div>
            <div className="absolute bottom-6 left-6 w-52">
                <button
                    className="flex items-center justify-center gap-2 w-full bg-orange-400 hover:bg-orange-500 text-white py-3 px-4 rounded-md transition-colors"
                    onClick={() => setShowAddForm(true)}
                >
                    <Plus className="h-5 w-5" />
                    <span className="font-medium">Add Product</span>
                </button>
            </div>

            {showAddForm && (
                <AddInventoryForm
                    onClose={() => setShowAddForm(false)}
                    onSubmit={handleAddInventory}
                    inventoryId={activeInventory?.inventory_id}
                />
            )}
        </div>
    )
}

export default Sidebar

