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

export const fetchUserProfile = async () => {
    try {
        // Since there's no specific user endpoint in the backend,
        // we'll use the first inventory owner as the user
        const inventoriesResponse = await api.get("/inventory/")
        const inventories = inventoriesResponse.data

        // If no inventories, return default user data
        if (!inventories || inventories.length === 0) {
            return {
                name: "Default User",
                avatar: "/placeholder.svg?height=80&width=80",
                id: "N/A",
                shelfId: "N/A",
                prevTheft: "None",
                location: "N/A",
            }
        }

        // Use the first inventory's owner as the user
        const inventory = inventories[0]

        return {
            name: inventory.owner.owner_name,
            avatar: "/placeholder.svg?height=80&width=80", // Default avatar
            id: inventory.owner.owner_id,
            shelfId: "N/A", // Not available from this endpoint
            prevTheft: inventory.previous_theft_count.toString(),
            location: inventory.location,
        }
    } catch (error) {
        console.error("Error fetching user profile:", error)
        throw error
    }
}

