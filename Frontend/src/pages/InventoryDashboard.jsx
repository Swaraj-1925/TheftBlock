"use client"

import { useState } from "react"
import { useOutletContext } from "react-router-dom"
import Dashboard from "../components/Dashboard"
import UserProfile from "../components/UserProfile"
import PastTheft from "../components/PastTheft"

function InventoryDashboard() {
    const { activeInventory, refreshTrigger } = useOutletContext()
    const [selectedProduct, setSelectedProduct] = useState(null)
    const [selectedTheft, setSelectedTheft] = useState(null)

    return (
        <div className="flex flex-col lg:flex-row gap-6">
            <div className="lg:w-3/4">
                <Dashboard
                    inventoryId={activeInventory?.inventory_id}
                    refreshTrigger={refreshTrigger}
                    onSelectProduct={setSelectedProduct}
                />
            </div>
            <div className="lg:w-1/4 flex flex-col gap-6">
                <UserProfile selectedProduct={selectedProduct} inventory={activeInventory} />
                <PastTheft
                    inventoryId={activeInventory?.inventory_id}
                    refreshTrigger={refreshTrigger}
                    onSelectTheft={setSelectedTheft}
                    selectedTheft={selectedTheft}
                />
            </div>
        </div>
    )
}

export default InventoryDashboard

