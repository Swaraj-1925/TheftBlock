import axios from "axios"

// Create axios instance with base URL and default headers
const api = axios.create({
    baseURL: "http://localhost:8000",
    headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
    },
})

// Add response interceptor for logging
api.interceptors.response.use(
    (response) => {
        console.log(`API Response [${response.config.method.toUpperCase()}] ${response.config.url}:`, response.data)
        return response
    },
    (error) => {
        console.error("API Error:", error.response || error.message || error)
        return Promise.reject(error)
    },
)

export const createSupplier = async (supplierName) => {
    try {
        const response = await api.post(`/supplier/create?supplier_name=${encodeURIComponent(supplierName)}`)
        return response.data
    } catch (error) {
        console.error("Error creating supplier:", error)
        throw error
    }
}

export const createSupplierReceipt = async (supplierId, inventoryId, products) => {
    try {
        const response = await api.post(
            `/supplier/create_receipt?supplier_id=${encodeURIComponent(supplierId)}&inventory_id=${encodeURIComponent(inventoryId)}`,
            {
                inventory_id: inventoryId,
                products: products,
                total_products: products.length,
            },
        )
        return response.data
    } catch (error) {
        console.error("Error creating supplier receipt:", error)
        throw error
    }
}

export const linkSupplierToInventory = async (supplierId, inventoryId) => {
    try {
        // Note: This endpoint might not exist in your API based on the provided files
        // You might need to implement it or use a different approach
        const response = await api.post("/supplier/link_to_inventory", {
            supplier_id: supplierId,
            inventory_id: inventoryId,
        })
        return response.data
    } catch (error) {
        console.error("Error linking supplier to inventory:", error)
        throw error
    }
}

