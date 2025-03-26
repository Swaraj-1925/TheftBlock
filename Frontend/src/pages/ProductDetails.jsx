"use client"

import { useState, useEffect } from "react"
import { useParams, useNavigate, useOutletContext } from "react-router-dom"
import { getProductDetails } from "../api/inventory.jsx"
import { Package, ArrowLeft } from "lucide-react"

function ProductDetails() {
    const { productId } = useParams()
    const navigate = useNavigate()
    const { activeInventory } = useOutletContext()
    const [product, setProduct] = useState(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    useEffect(() => {
        const fetchProductDetails = async () => {
            try {
                setLoading(true)
                const data = await getProductDetails(productId)
                setProduct(data)
                setError(null)
            } catch (err) {
                console.error("Error fetching product details:", err)
                setError("Failed to load product details. Please try again.")
            } finally {
                setLoading(false)
            }
        }

        if (productId) {
            fetchProductDetails()
        }
    }, [productId])

    if (loading) {
        return (
            <div className="bg-white rounded-lg shadow-md p-6 animate-pulse">
                <div className="flex justify-between items-center mb-4">
                    <div className="h-6 bg-gray-200 rounded w-1/4"></div>
                    <div className="h-6 bg-gray-200 rounded w-8"></div>
                </div>
                <div className="flex flex-col items-center mb-6">
                    <div className="w-24 h-24 bg-gray-200 rounded-lg mb-3"></div>
                    <div className="h-5 bg-gray-200 rounded w-1/3 mb-1"></div>
                    <div className="h-4 bg-gray-200 rounded w-1/4"></div>
                </div>
                <div className="space-y-3">
                    {[...Array(6)].map((_, i) => (
                        <div key={i} className="h-4 bg-gray-200 rounded"></div>
                    ))}
                </div>
            </div>
        )
    }

    if (error) {
        return (
            <div className="bg-white rounded-lg shadow-md p-6">
                <div className="text-red-500 mb-4">{error}</div>
                <button onClick={() => navigate("/")} className="flex items-center text-blue-500 hover:underline">
                    <ArrowLeft className="h-4 w-4 mr-1" />
                    Back to Dashboard
                </button>
            </div>
        )
    }

    if (!product) {
        return (
            <div className="bg-white rounded-lg shadow-md p-6">
                <div className="text-gray-500 mb-4">Product not found</div>
                <button onClick={() => navigate("/")} className="flex items-center text-blue-500 hover:underline">
                    <ArrowLeft className="h-4 w-4 mr-1" />
                    Back to Dashboard
                </button>
            </div>
        )
    }

    return (
        <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex justify-between items-center mb-4">
                <h2 className="text-2xl font-bold">Product Details</h2>
                <button onClick={() => navigate("/")} className="flex items-center text-blue-500 hover:underline">
                    <ArrowLeft className="h-4 w-4 mr-1" />
                    Back to Dashboard
                </button>
            </div>

            <div className="flex flex-col md:flex-row gap-6">
                <div className="md:w-1/3 flex flex-col items-center">
                    <div className="w-32 h-32 bg-gray-100 rounded-lg flex items-center justify-center mb-4">
                        <Package className="h-16 w-16 text-gray-400" />
                    </div>
                    <h3 className="text-xl font-medium text-blue-800">{product.name || product.product_name}</h3>
                    <p className="text-sm text-gray-500">{product.id || product.product_id}</p>

                    <div className="mt-4 p-3 bg-gray-50 rounded-md w-full">
                        <h4 className="font-medium mb-2">Quick Info</h4>
                        <div className="grid grid-cols-2 gap-2 text-sm">
                            <div className="text-gray-500">Price:</div>
                            <div className="font-medium">${product.price?.toLocaleString()}</div>
                            <div className="text-gray-500">Status:</div>
                            <div className="font-medium">{product.status}</div>
                            <div className="text-gray-500">RFID:</div>
                            <div className="font-medium">{product.rfid_tag}</div>
                        </div>
                    </div>
                </div>

                <div className="md:w-2/3">
                    <div className="space-y-4">
                        <div>
                            <h4 className="text-lg font-medium mb-2">Product Information</h4>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div className="p-3 bg-gray-50 rounded-md">
                                    <div className="text-sm text-gray-500">Location</div>
                                    <div className="font-medium">{product.location}</div>
                                </div>
                                <div className="p-3 bg-gray-50 rounded-md">
                                    <div className="text-sm text-gray-500">Supplier ID</div>
                                    <div className="font-medium">{product.supplier_id}</div>
                                </div>
                                <div className="p-3 bg-gray-50 rounded-md">
                                    <div className="text-sm text-gray-500">Shelf ID</div>
                                    <div className="font-medium">{product.shelf_id || "Not on shelf"}</div>
                                </div>
                                <div className="p-3 bg-gray-50 rounded-md">
                                    <div className="text-sm text-gray-500">Last Updated</div>
                                    <div className="font-medium">
                                        {product.last_updated ? new Date(product.last_updated).toLocaleString() : "Unknown"}
                                    </div>
                                </div>
                            </div>
                        </div>

                        {product.description && (
                            <div>
                                <h4 className="text-lg font-medium mb-2">Description</h4>
                                <p className="text-gray-700 bg-gray-50 p-3 rounded-md">{product.description}</p>
                            </div>
                        )}

                        <div>
                            <h4 className="text-lg font-medium mb-2">Inventory Information</h4>
                            <p className="text-gray-700 bg-gray-50 p-3 rounded-md">
                                This product is part of inventory: <strong>{activeInventory?.inventory_id || "Unknown"}</strong>
                                <br />
                                Location: <strong>{activeInventory?.location || "Unknown"}</strong>
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default ProductDetails

