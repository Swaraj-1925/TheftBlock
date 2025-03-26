"use client"

import { useState, useEffect } from "react"
import { X } from "lucide-react"
import { ProductStatus } from "../constants/productStatus"
import { createTestProducts, createTestProductsForInventory } from "../api/inventory"
import { createSupplier } from "../api/supplier"

const AddInventoryForm = ({ onClose, onSubmit, inventoryId }) => {
    const [formType, setFormType] = useState("product")
    const [productForm, setProductForm] = useState({
        productName: "",
        rfidTag: "",
        price: "",
        supplierId: "",
        status: ProductStatus.ON_SHELF,
        location: "",
        shelfId: "",
    })
    const [testForm, setTestForm] = useState({
        numProducts: 5,
        supplierName: "",
        supplierId: "",
        inventoryId: inventoryId || "",
        createForInventory: !!inventoryId,
    })
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)
    const [success, setSuccess] = useState(null)

    // Update inventoryId when it changes
    useEffect(() => {
        if (inventoryId) {
            setTestForm((prev) => ({
                ...prev,
                inventoryId,
                createForInventory: true,
            }))
        }
    }, [inventoryId])

    const handleProductChange = (e) => {
        const { name, value } = e.target
        setProductForm((prev) => ({ ...prev, [name]: value }))
    }

    const handleTestChange = (e) => {
        const { name, value, type } = e.target

        if (type === "checkbox") {
            const checked = e.target.checked
            setTestForm((prev) => ({ ...prev, [name]: checked }))
        } else {
            setTestForm((prev) => ({ ...prev, [name]: value }))
        }
    }

    const handleProductSubmit = (e) => {
        e.preventDefault()
        onSubmit({
            ...productForm,
            price: Number.parseFloat(productForm.price),
            inventoryId: inventoryId,
        })
    }

    const handleTestSubmit = async (e) => {
        e.preventDefault()
        setLoading(true)
        setError(null)
        setSuccess(null)

        try {
            // If supplier ID is empty, create a new supplier
            let supplierId = testForm.supplierId
            if (!supplierId && testForm.supplierName) {
                const supplier = await createSupplier(testForm.supplierName)
                supplierId = supplier.supplier_id
            }

            if (!supplierId) {
                throw new Error("Supplier ID is required")
            }

            let result
            if (testForm.createForInventory && testForm.inventoryId) {
                result = await createTestProductsForInventory(
                    testForm.numProducts,
                    testForm.supplierName,
                    supplierId,
                    testForm.inventoryId,
                )
                setSuccess(`Created ${testForm.numProducts} test products for inventory ${testForm.inventoryId}`)
            } else {
                result = await createTestProducts(testForm.numProducts, testForm.supplierName, supplierId)
                setSuccess(`Created ${testForm.numProducts} test products`)
            }

            console.log("Test products created:", result)

            // Wait 1 second before closing the form
            setTimeout(() => {
                onClose()
                // Trigger refresh instead of page reload
                window.dispatchEvent(new CustomEvent("inventory-updated"))
            }, 1000)
        } catch (err) {
            console.error("Error creating test products:", err)
            setError(err instanceof Error ? err.message : "Failed to create test products")
        } finally {
            setLoading(false)
        }
    }

    // Check if location fields should be shown
    const showLocationFields = productForm.status === ProductStatus.ON_SHELF

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md">
                <div className="flex justify-between items-center mb-4">
                    <h2 className="text-xl font-bold">Add Product</h2>
                    <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
                        <X className="h-5 w-5" />
                    </button>
                </div>

                <div className="mb-4">
                    <div className="flex border-b">
                        <button
                            className={`py-2 px-4 ${formType === "product" ? "border-b-2 border-blue-500 text-blue-600" : "text-gray-500"}`}
                            onClick={() => setFormType("product")}
                        >
                            Add Single Product
                        </button>
                        <button
                            className={`py-2 px-4 ${formType === "test" ? "border-b-2 border-blue-500 text-blue-600" : "text-gray-500"}`}
                            onClick={() => setFormType("test")}
                        >
                            Generate Test Data
                        </button>
                    </div>
                </div>

                {error && <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">{error}</div>}

                {success && (
                    <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">{success}</div>
                )}

                {formType === "product" ? (
                    <form onSubmit={handleProductSubmit}>
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Product Name</label>
                                <input
                                    type="text"
                                    name="productName"
                                    value={productForm.productName}
                                    onChange={handleProductChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                                    required
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">RFID Tag</label>
                                <input
                                    type="text"
                                    name="rfidTag"
                                    value={productForm.rfidTag}
                                    onChange={handleProductChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                                    required
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Price</label>
                                <input
                                    type="number"
                                    name="price"
                                    value={productForm.price}
                                    onChange={handleProductChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                                    min="0"
                                    step="0.01"
                                    required
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
                                <select
                                    name="status"
                                    value={productForm.status}
                                    onChange={handleProductChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                                    required
                                >
                                    <option value={ProductStatus.ON_SHELF}>On Shelf</option>
                                    <option value={ProductStatus.SOLD}>Sold</option>
                                    <option value={ProductStatus.MISSING}>Missing (Theft)</option>
                                    <option value={ProductStatus.OUT_SHELF}>Out of Shelf</option>
                                    <option value={ProductStatus.WITH_SUPPLIER}>With Supplier</option>
                                </select>
                            </div>

                            {/* Show location fields only when status is ON_SHELF */}
                            {showLocationFields && (
                                <>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">Shelf ID</label>
                                        <input
                                            type="text"
                                            name="shelfId"
                                            value={productForm.shelfId}
                                            onChange={handleProductChange}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-md"
                                            placeholder="e.g., A1, B2, etc."
                                        />
                                    </div>

                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">Location Description</label>
                                        <input
                                            type="text"
                                            name="location"
                                            value={productForm.location}
                                            onChange={handleProductChange}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-md"
                                            placeholder="e.g., North Wing, Section 3, etc."
                                        />
                                    </div>
                                </>
                            )}

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Supplier ID</label>
                                <input
                                    type="text"
                                    name="supplierId"
                                    value={productForm.supplierId}
                                    onChange={handleProductChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                                    required
                                />
                            </div>

                            {inventoryId && (
                                <div className="bg-blue-50 p-3 rounded-md">
                                    <p className="text-sm text-blue-700">
                                        This product will be added to inventory: <strong>{inventoryId}</strong>
                                    </p>
                                </div>
                            )}
                        </div>

                        <div className="mt-6 flex justify-end space-x-3">
                            <button
                                type="button"
                                onClick={onClose}
                                className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                            >
                                Cancel
                            </button>
                            <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
                                Add Product
                            </button>
                        </div>
                    </form>
                ) : (
                    <form onSubmit={handleTestSubmit}>
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Number of Products</label>
                                <input
                                    type="number"
                                    name="numProducts"
                                    value={testForm.numProducts}
                                    onChange={handleTestChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                                    min="1"
                                    max="100"
                                    required
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Supplier Name</label>
                                <input
                                    type="text"
                                    name="supplierName"
                                    value={testForm.supplierName}
                                    onChange={handleTestChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                                    required
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Supplier ID (leave empty to create new)
                                </label>
                                <input
                                    type="text"
                                    name="supplierId"
                                    value={testForm.supplierId}
                                    onChange={handleTestChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                                />
                            </div>

                            <div className="flex items-center">
                                <input
                                    type="checkbox"
                                    id="createForInventory"
                                    name="createForInventory"
                                    checked={testForm.createForInventory}
                                    onChange={handleTestChange}
                                    className="h-4 w-4 text-blue-600 border-gray-300 rounded"
                                />
                                <label htmlFor="createForInventory" className="ml-2 block text-sm text-gray-700">
                                    Create for specific inventory
                                </label>
                            </div>

                            {testForm.createForInventory && (
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Inventory ID</label>
                                    <input
                                        type="text"
                                        name="inventoryId"
                                        value={testForm.inventoryId}
                                        onChange={handleTestChange}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-md"
                                        required={testForm.createForInventory}
                                    />
                                </div>
                            )}
                        </div>

                        <div className="mt-6 flex justify-end space-x-3">
                            <button
                                type="button"
                                onClick={onClose}
                                className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                                disabled={loading}
                            >
                                Cancel
                            </button>
                            <button
                                type="submit"
                                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-blue-300"
                                disabled={loading}
                            >
                                {loading ? "Creating..." : "Generate Test Data"}
                            </button>
                        </div>
                    </form>
                )}
            </div>
        </div>
    )
}

export default AddInventoryForm

