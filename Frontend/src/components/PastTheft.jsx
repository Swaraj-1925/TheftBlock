"use client"

import { useState, useEffect } from "react"
import { fetchPastThefts, getTheftDetails } from "../api/theft.jsx"
import { AlertTriangle, ChevronLeft } from "lucide-react"

const PastTheft = ({ inventoryId, refreshTrigger, onSelectTheft, selectedTheft }) => {
    const [theftRecords, setTheftRecords] = useState([])
    const [loading, setLoading] = useState(true)
    const [detailedTheft, setDetailedTheft] = useState(null)
    const [detailView, setDetailView] = useState(false)
    const [error, setError] = useState(null)

    useEffect(() => {
        const getTheftRecords = async () => {
            try {
                setLoading(true)
                const data = await fetchPastThefts(inventoryId)
                setTheftRecords(data)
                setError(null)
            } catch (error) {
                console.error("Error fetching theft records:", error)
                setError("Failed to load theft records")
            } finally {
                setLoading(false)
            }
        }

        getTheftRecords()
    }, [inventoryId, refreshTrigger])

    // Listen for theft added events
    useEffect(() => {
        const handleTheftAdded = () => {
            const getTheftRecords = async () => {
                try {
                    const data = await fetchPastThefts(inventoryId)
                    setTheftRecords(data)
                } catch (error) {
                    console.error("Error refreshing theft records:", error)
                }
            }

            getTheftRecords()
        }

        window.addEventListener("theft-added", handleTheftAdded)

        return () => {
            window.removeEventListener("theft-added", handleTheftAdded)
        }
    }, [inventoryId])

    useEffect(() => {
        // When a theft is selected, fetch its details
        if (selectedTheft) {
            const getTheftData = async () => {
                try {
                    setLoading(true)
                    const data = await getTheftDetails(selectedTheft.id)
                    setDetailedTheft(data)
                    setDetailView(true)
                    setError(null)
                } catch (error) {
                    console.error("Error fetching theft details:", error)
                    setError("Failed to load theft details")
                } finally {
                    setLoading(false)
                }
            }

            getTheftData()
        }
    }, [selectedTheft])

    const handleTheftClick = (theft) => {
        if (onSelectTheft) {
            onSelectTheft(theft)
        } else {
            // If no external handler, handle internally
            setDetailedTheft(theft)
            setDetailView(true)
        }
    }

    const handleBackClick = () => {
        setDetailView(false)
        setDetailedTheft(null)
        if (onSelectTheft) {
            onSelectTheft(null)
        }
    }

    if (loading) {
        return (
            <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-2xl font-bold mb-4">Past Theft</h2>
                <div className="space-y-3 animate-pulse">
                    {[...Array(3)].map((_, i) => (
                        <div key={i} className="h-12 bg-gray-100 rounded"></div>
                    ))}
                </div>
            </div>
        )
    }

    return (
        <div className="bg-white rounded-lg shadow-md p-6">
            {error && <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">{error}</div>}

            {detailView && detailedTheft ? (
                <>
                    <div className="flex items-center justify-between mb-4">
                        <button onClick={handleBackClick} className="flex items-center text-blue-500 hover:underline">
                            <ChevronLeft className="h-4 w-4 mr-1" />
                            Back
                        </button>
                        <h2 className="text-xl font-bold">Theft Details</h2>
                        <AlertTriangle className="h-5 w-5 text-red-500" />
                    </div>

                    <div className="mb-4">
                        <h3 className="text-lg font-semibold text-red-600">{detailedTheft.productName}</h3>
                        <p className="text-sm text-gray-500">ID: {detailedTheft.productId}</p>
                    </div>

                    <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                            <span className="font-medium">Date:</span>
                            <span>{detailedTheft.date}</span>
                        </div>
                        <div className="flex justify-between">
                            <span className="font-medium">Time:</span>
                            <span>{detailedTheft.time}</span>
                        </div>
                        <div className="flex justify-between">
                            <span className="font-medium">Location:</span>
                            <span>{detailedTheft.location}</span>
                        </div>
                        <div className="flex justify-between">
                            <span className="font-medium">Value:</span>
                            <span>${detailedTheft.value?.toLocaleString()}</span>
                        </div>
                        <div className="flex justify-between">
                            <span className="font-medium">Status:</span>
                            <span>{detailedTheft.status}</span>
                        </div>
                        <div className="flex justify-between">
                            <span className="font-medium">Reported By:</span>
                            <span>{detailedTheft.reportedBy}</span>
                        </div>
                        {detailedTheft.notes && (
                            <div className="pt-2">
                                <p className="font-medium">Notes:</p>
                                <p className="text-gray-600 mt-1 bg-gray-50 p-2 rounded">{detailedTheft.notes}</p>
                            </div>
                        )}
                        {detailedTheft.rfidLastSeen && (
                            <div className="flex justify-between">
                                <span className="font-medium">RFID Last Seen:</span>
                                <span>{new Date(detailedTheft.rfidLastSeen).toLocaleString()}</span>
                            </div>
                        )}
                    </div>
                </>
            ) : (
                <>
                    <h2 className="text-2xl font-bold mb-4">Past Theft</h2>

                    {theftRecords.length === 0 ? (
                        <p className="text-gray-500 text-center py-4">No theft records found</p>
                    ) : (
                        <div className="space-y-3">
                            {theftRecords.map((record) => (
                                <div
                                    key={record.id}
                                    className="p-3 bg-gray-50 rounded-md cursor-pointer hover:bg-gray-100"
                                    onClick={() => handleTheftClick(record)}
                                >
                                    <div className="flex justify-between">
                                        <span className="font-medium">{record.productName}</span>
                                        <span className="text-sm text-gray-500">{record.date}</span>
                                    </div>
                                    <div className="text-sm text-gray-500">
                                        <span>ID: {record.productId}</span>
                                        <span className="mx-2">•</span>
                                        <span>{record.location}</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </>
            )}
        </div>
    )
}

export default PastTheft

