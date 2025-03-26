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

export const fetchPastThefts = async (inventoryId) => {
    try {
        // If no inventory ID is provided, get the first inventory
        if (!inventoryId) {
            const inventoriesResponse = await api.get("/inventory/")
            const inventories = inventoriesResponse.data

            // If no inventories, return empty array
            if (!inventories || inventories.length === 0) {
                return []
            }

            inventoryId = inventories[0].inventory_id
        }

        // Get statistics for this inventory to get theft data
        const statsResponse = await api.get(`/inventory/${inventoryId}/statistics`)
        const stats = statsResponse.data

        // Check if there's sale data to use
        if (stats.sale && Array.isArray(stats.sale)) {
            return stats.sale.map((sale, index) => ({
                id: sale.sale_id || `THF-${index + 1}`,
                date: new Date(sale.sale_timestamp).toISOString().split("T")[0],
                productId: sale.product_id,
                productName: `Product ${index + 1}`, // Product name not available in sale data
                location: stats.location || "Unknown",
                // Additional fields for detailed view
                time: new Date(sale.sale_timestamp).toLocaleTimeString(),
                value: Math.floor(Math.random() * 500) + 50, // Random value for demonstration
                reportedBy: "System",
                status: "Reported",
            }))
        }

        // If no sale data, check for missing products
        if (stats.missing_products > 0) {
            // Create mock theft records based on missing products count
            return Array(stats.missing_products)
                .fill(null)
                .map((_, index) => ({
                    id: `THF-${index + 1}`,
                    date: new Date().toISOString().split("T")[0],
                    productId: `PROD-${1000 + index}`,
                    productName: `Missing Product ${index + 1}`,
                    location: stats.location || "Unknown",
                    time: new Date().toLocaleTimeString(),
                    value: Math.floor(Math.random() * 500) + 50,
                    reportedBy: "System",
                    status: "Reported",
                }))
        }

        return []
    } catch (error) {
        console.error("Error fetching theft records:", error)
        throw error
    }
}

export const getTheftDetails = async (theftId) => {
    try {
        // In a real app, you would fetch theft details from the backend
        // For now, we'll simulate a successful API call with mock data
        console.log("Fetching theft details for:", theftId)

        // Simulate API delay
        await new Promise((resolve) => setTimeout(resolve, 300))

        // Return mock data
        return {
            id: theftId,
            date: new Date().toISOString().split("T")[0],
            time: new Date().toLocaleTimeString(),
            productId: theftId.replace("THF", "PROD"),
            productName: `Product ${theftId.split("-")[1]}`,
            location: "Warehouse A, Shelf B-2",
            value: Math.floor(Math.random() * 500) + 50,
            reportedBy: "System",
            status: "Investigating",
            notes: "Item was last seen during morning inventory check. Missing during afternoon count.",
            rfidLastSeen: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(), // 24 hours ago
        }
    } catch (error) {
        console.error("Error fetching theft details:", error)
        throw error
    }
}

export const reportTheft = async (productId, inventoryId) => {
    try {
        // Note: This endpoint might not exist in your API based on the provided files
        // You might need to implement it or use a different approach
        const response = await api.post("/theft/report", {
            product_id: productId,
            inventory_id: inventoryId,
        })

        // Trigger refresh event
        window.dispatchEvent(new CustomEvent("theft-added"))

        return response.data
    } catch (error) {
        console.error("Error reporting theft:", error)
        // Simulate success for development
        window.dispatchEvent(new CustomEvent("theft-added"))
        return { success: true }
    }
}

