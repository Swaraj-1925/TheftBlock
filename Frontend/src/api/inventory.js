import axios from "axios"
import { ProductStatus } from "../constants/productStatus"

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

// Add request interceptor for logging
api.interceptors.request.use(
    (config) => {
        console.log(`API Request [${config.method.toUpperCase()}] ${config.url}`)
        return config
    },
    (error) => {
        return Promise.reject(error)
    },
)

export const fetchInventories = async () => {
    try {
        const response = await api.get("/inventory/")
        return response.data
    } catch (error) {
        console.error("Error fetching inventories:", error)
        throw error
    }
}

export const fetchInventoryData = async (inventoryId) => {
    try {
        // If no inventory ID is provided, get the first inventory
        if (!inventoryId) {
            const inventories = await fetchInventories()

            // If no inventories, return empty data
            if (!inventories || inventories.length === 0) {
                return {
                    totalProducts: 0,
                    onShelf: 0,
                    theftCount: 0,
                    items: [],
                }
            }

            inventoryId = inventories[0].inventory_id
        }

        // Get products for this inventory
        const productsResponse = await api.get(`/inventory/${inventoryId}/products`)
        const productsData = productsResponse.data

        // Get statistics for this inventory
        const statsResponse = await api.get(`/inventory/${inventoryId}/statistics`)
        const stats = statsResponse.data

        // Map the products to our frontend model
        const items = productsData.products.map((product) => ({
            id: product.product_id,
            name: product.product_name,
            quantity: 1, // Each product is a single item with RFID
            location: product.shelf_id ? `Shelf ${product.shelf_id}` : "Not on shelf",
            status: product.status,
            price: product.price,
            rfid_tag: product.rfid_tag,
            supplier_id: product.supplier_id,
            // Add additional fields that might be useful
            shelf_id: product.shelf_id,
            rack_id: product.rack_id,
        }))

        return {
            totalProducts: stats.products_on_shelf || 0,
            onShelf: stats.products_on_shelf || 0,
            theftCount: stats.missing_products || 0,
            items: items,
        }
    } catch (error) {
        console.error("Error fetching inventory data:", error)
        throw error
    }
}

export const fetchInventoryStatistics = async (inventoryId) => {
    try {
        if (!inventoryId) {
            const inventories = await fetchInventories()

            if (!inventories || inventories.length === 0) {
                throw new Error("No inventories found")
            }

            inventoryId = inventories[0].inventory_id
        }

        const response = await api.get(`/inventory/${inventoryId}/statistics`)
        return response.data
    } catch (error) {
        console.error("Error fetching inventory statistics:", error)
        throw error
    }
}

export const addInventoryItem = async (item) => {
    try {
        // For now, we'll simulate a successful API call
        // In a real implementation, you would send this to your backend
        console.log("Adding inventory item:", item)

        // If the status is "missing", add it to theft records
        if (item.status === ProductStatus.MISSING) {
            // Trigger an event to update theft records
            window.dispatchEvent(
                new CustomEvent("theft-added", {
                    detail: {
                        productId: `PROD-${Math.floor(Math.random() * 10000)}`,
                        productName: item.productName,
                        date: new Date().toISOString().split("T")[0],
                        location: item.location || "Unknown",
                    },
                }),
            )
        }

        // Simulate API delay
        await new Promise((resolve) => setTimeout(resolve, 500))

        // Trigger refresh event
        window.dispatchEvent(new CustomEvent("inventory-updated"))

        return { success: true, message: "Item added successfully" }
    } catch (error) {
        console.error("Error adding inventory item:", error)
        throw error
    }
}

export const createTestProducts = async (numProducts, supplierName, supplierId) => {
    try {
        const response = await api.post(
            `/test/create_products?num_products=${numProducts}&supplier_name=${encodeURIComponent(supplierName)}&supplier_id=${encodeURIComponent(supplierId)}`,
        )

        // Trigger refresh event
        window.dispatchEvent(new CustomEvent("inventory-updated"))

        return response.data
    } catch (error) {
        console.error("Error creating test products:", error)
        throw error
    }
}

export const createTestProductsForInventory = async (numProducts, supplierName, supplierId, inventoryId) => {
    try {
        const response = await api.post(
            `/test/${inventoryId}/create_products?num_products=${numProducts}&supplier_name=${encodeURIComponent(supplierName)}&supplier_id=${encodeURIComponent(supplierId)}`,
        )

        // Trigger refresh event
        window.dispatchEvent(new CustomEvent("inventory-updated"))

        return response.data
    } catch (error) {
        console.error("Error creating test products for inventory:", error)
        throw error
    }
}

export const getProductDetails = async (productId) => {
    try {
        // In a real implementation, you would have an endpoint for product details
        // For now, we'll extract it from the inventory data
        const inventories = await fetchInventories()
        if (!inventories || inventories.length === 0) {
            throw new Error("No inventories found")
        }

        // Try to find the product in each inventory
        for (const inventory of inventories) {
            try {
                const productsResponse = await api.get(`/inventory/${inventory.inventory_id}/products`)
                const productsData = productsResponse.data

                const product = productsData.products.find((p) => p.product_id === productId)
                if (product) {
                    return {
                        id: product.product_id,
                        name: product.product_name,
                        price: product.price,
                        status: product.status,
                        location: product.shelf_id ? `Shelf ${product.shelf_id}` : "Not on shelf",
                        rfid_tag: product.rfid_tag,
                        supplier_id: product.supplier_id,
                        shelf_id: product.shelf_id,
                        rack_id: product.rack_id,
                        description: "No description available", // Add default description
                        last_updated: new Date().toISOString(),
                    }
                }
            } catch (err) {
                console.error(`Error searching for product in inventory ${inventory.inventory_id}:`, err)
            }
        }

        throw new Error(`Product with ID ${productId} not found`)
    } catch (error) {
        console.error("Error fetching product details:", error)
        throw error
    }
}

export const moveProductToShelf = async (productId, shelfId) => {
    try {
        const response = await api.post("/inventory/move_product", {
            product_id: productId,
            target_shelf_id: shelfId,
        })

        // Trigger refresh event
        window.dispatchEvent(new CustomEvent("inventory-updated"))

        return response.data
    } catch (error) {
        console.error("Error moving product:", error)
        throw error
    }
}

export const scanShelf = async (shelfId) => {
    try {
        const response = await api.get(`/inventory/scan_shelf/${shelfId}`)

        // Trigger refresh event
        window.dispatchEvent(new CustomEvent("inventory-updated"))

        return response.data
    } catch (error) {
        console.error("Error scanning shelf:", error)
        throw error
    }
}

export const sellProduct = async (productId, inventoryId) => {
    try {
        const response = await api.post("/inventory/sell_product", {
            product_id: productId,
            inventory_id: inventoryId,
        })

        // Trigger refresh event
        window.dispatchEvent(new CustomEvent("inventory-updated"))

        return response.data
    } catch (error) {
        console.error("Error selling product:", error)
        throw error
    }
}

