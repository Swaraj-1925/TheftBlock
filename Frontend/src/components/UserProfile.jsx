"use client"

import { useState, useEffect } from "react"
import { fetchUserProfile } from "../api/user"
import { getProductDetails } from "../api/inventory"
import { Package, User } from "lucide-react"

const UserProfile = ({ selectedProduct, inventory }) => {
    const [userData, setUserData] = useState(null)
    const [productData, setProductData] = useState(null)
    const [loading, setLoading] = useState(true)
    const [view, setView] = useState("user") // 'user' or 'product'
    const [error, setError] = useState(null)

    useEffect(() => {
        const getUserData = async () => {
            try {
                setLoading(true)
                const data = await fetchUserProfile()
                setUserData(data)
                setError(null)
            } catch (error) {
                console.error("Error fetching user data:", error)
                setError("Failed to load user profile")
            } finally {
                setLoading(false)
            }
        }

        getUserData()
    }, [inventory])

    useEffect(() => {
        // When a product is selected, fetch its details and switch to product view
        if (selectedProduct) {
            const getProductData = async () => {
                try {
                    setLoading(true)
                    // If we already have all the product details, use them
                    if (selectedProduct.description) {
                        setProductData(selectedProduct)
                    } else {
                        // Otherwise fetch more details
                        const data = await getProductDetails(selectedProduct.id)
                        setProductData(data)
                    }
                    setView("product")
                    setError(null)
                } catch (error) {
                    console.error("Error fetching product data:", error)
                    setError("Failed to load product details")
                } finally {
                    setLoading(false)
                }
            }

            getProductData()
        } else {
            // If no product is selected, show user profile
            setView("user")
            setProductData(null)
        }
    }, [selectedProduct])

    if (loading) {
        return (
            <div className="bg-white rounded-lg shadow-md p-6 animate-pulse">
                <div className="flex flex-col items-center mb-4">
                    <div className="w-20 h-20 bg-gray-200 rounded-full mb-2"></div>
                    <div className="h-4 bg-gray-200 rounded w-24 mb-1"></div>
                </div>
                <div className="space-y-2">
                    {[...Array(4)].map((_, i) => (
                        <div key={i} className="h-4 bg-gray-200 rounded"></div>
                    ))}
                </div>
            </div>
        )
    }

    return (
        <div className="bg-white rounded-lg shadow-md p-6">
            {error && <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">{error}</div>}

            {view === "user" && userData && (
                <>
                    <div className="flex justify-between items-center mb-4">
                        <h3 className="text-lg font-semibold">User Profile</h3>
                        <User className="h-5 w-5 text-blue-500" />
                    </div>
                    <div className="flex flex-col items-center mb-4">
                        <img
                            src={userData.avatar || "/placeholder.svg?height=80&width=80"}
                            alt={userData.name}
                            className="w-20 h-20 rounded-full object-cover mb-2"
                        />
                        <h3 className="text-lg font-medium text-blue-800">{userData.name}</h3>
                    </div>
                    <div className="space-y-2">
                        <p>
                            <span className="font-medium">Id:</span> {userData.id}
                        </p>
                        <p>
                            <span className="font-medium">Shelf id:</span> {userData.shelfId}
                        </p>
                        <p>
                            <span className="font-medium">Prev Theft:</span> {userData.prevTheft}
                        </p>
                        <p>
                            <span className="font-medium">Location:</span> {userData.location}
                        </p>
                    </div>
                    {inventory && (
                        <div className="mt-4 pt-4 border-t border-gray-100">
                            <p>
                                <span className="font-medium">Current Inventory:</span> {inventory.name}
                            </p>
                            <p>
                                <span className="font-medium">Inventory ID:</span> {inventory.inventory_id}
                            </p>
                        </div>
                    )}
                </>
            )}

            {view === "product" && productData && (
                <>
                    <div className="flex justify-between items-center mb-4">
                        <h3 className="text-lg font-semibold">Product Details</h3>
                        <button
                            onClick={() => {
                                setView("user")
                                setProductData(null)
                            }}
                            className="text-xs text-blue-500 hover:underline"
                        >
                            Back to User
                        </button>
                        <Package className="h-5 w-5 text-blue-500" />
                    </div>
                    <div className="flex flex-col items-center mb-4">
                        <div className="w-20 h-20 bg-gray-100 rounded-lg flex items-center justify-center mb-2">
                            <Package className="h-10 w-10 text-gray-400" />
                        </div>
                        <h3 className="text-lg font-medium text-blue-800">{productData.name}</h3>
                        <p className="text-sm text-gray-500">{productData.id}</p>
                    </div>
                    <div className="space-y-2">
                        <p>
                            <span className="font-medium">Price:</span> ${productData.price?.toLocaleString()}
                        </p>
                        <p>
                            <span className="font-medium">Status:</span> {productData.status}
                        </p>
                        <p>
                            <span className="font-medium">Location:</span> {productData.location}
                        </p>
                        <p>
                            <span className="font-medium">RFID Tag:</span> {productData.rfid_tag}
                        </p>
                        <p>
                            <span className="font-medium">Supplier ID:</span> {productData.supplier_id}
                        </p>
                        {productData.description && (
                            <p>
                                <span className="font-medium">Description:</span> {productData.description}
                            </p>
                        )}
                        {productData.last_updated && (
                            <p>
                                <span className="font-medium">Last Updated:</span> {new Date(productData.last_updated).toLocaleString()}
                            </p>
                        )}
                    </div>
                </>
            )}
        </div>
    )
}

export default UserProfile

