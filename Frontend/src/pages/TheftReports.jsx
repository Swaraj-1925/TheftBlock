"use client"

import { useState, useEffect } from "react"
import { useOutletContext } from "react-router-dom"
import { fetchPastThefts } from "../api/theft"
import { AlertTriangle, Search } from "lucide-react"

function TheftReports() {
    const { activeInventory, refreshTrigger } = useOutletContext()
    const [theftRecords, setTheftRecords] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)
    const [selectedTheft, setSelectedTheft] = useState(null)
    const [searchTerm, setSearchTerm] = useState("")

    useEffect(() => {
        const getTheftRecords = async () => {
            try {
                setLoading(true)
                const data = await fetchPastThefts(activeInventory?.inventory_id)
                setTheftRecords(data)
                setError(null)
            } catch (err) {
                console.error("Error fetching theft records:", err)
                setError("Failed to load theft records. Please try again.")
            } finally {
                setLoading(false)
            }
        }

        getTheftRecords()
    }, [activeInventory?.inventory_id, refreshTrigger])

    const filteredRecords = theftRecords.filter(
        (record) =>
            record.productName?.toLowerCase().includes(searchTerm.toLowerCase()) ||
            record.productId?.toLowerCase().includes(searchTerm.toLowerCase()) ||
            record.location?.toLowerCase().includes(searchTerm.toLowerCase()),
    )

    if (loading) {
        return (
            <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-2xl font-bold mb-4">Theft Reports</h2>
                <div className="space-y-3 animate-pulse">
                    {[...Array(5)].map((_, i) => (
                        <div key={i} className="h-16 bg-gray-100 rounded"></div>
                    ))}
                </div>
            </div>
        )
    }

    if (error) {
        return (
            <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-2xl font-bold mb-4">Theft Reports</h2>
                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">{error}</div>
            </div>
        )
    }

    return (
        <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold">Theft Reports</h2>
                <div className="flex items-center bg-gray-100 rounded-md px-3 py-2">
                    <Search className="h-4 w-4 text-gray-500 mr-2" />
                    <input
                        type="text"
                        placeholder="Search reports..."
                        className="bg-transparent border-none focus:outline-none text-sm"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                </div>
            </div>

            {selectedTheft ? (
                <div>
                    <button
                        onClick={() => setSelectedTheft(null)}
                        className="text-blue-500 hover:underline mb-4 flex items-center"
                    >
                        ← Back to all reports
                    </button>

                    <div className="bg-red-50 border border-red-100 rounded-lg p-4 mb-6">
                        <div className="flex items-center mb-3">
                            <AlertTriangle className="h-5 w-5 text-red-500 mr-2" />
                            <h3 className="text-lg font-semibold text-red-700">{selectedTheft.productName}</h3>
                        </div>
                        <p className="text-sm text-gray-600 mb-2">
                            Product ID: <span className="font-medium">{selectedTheft.productId}</span>
                        </p>
                        <p className="text-sm text-gray-600 mb-2">
                            Date: <span className="font-medium">{selectedTheft.date}</span> at{" "}
                            <span className="font-medium">{selectedTheft.time}</span>
                        </p>
                        <p className="text-sm text-gray-600 mb-2">
                            Location: <span className="font-medium">{selectedTheft.location}</span>
                        </p>
                        <p className="text-sm text-gray-600 mb-2">
                            Value: <span className="font-medium">${selectedTheft.value?.toLocaleString()}</span>
                        </p>
                        <p className="text-sm text-gray-600 mb-2">
                            Status: <span className="font-medium">{selectedTheft.status}</span>
                        </p>
                        <p className="text-sm text-gray-600">
                            Reported By: <span className="font-medium">{selectedTheft.reportedBy}</span>
                        </p>

                        {selectedTheft.notes && (
                            <div className="mt-4 p-3 bg-white rounded border border-gray-200">
                                <p className="text-sm font-medium mb-1">Notes:</p>
                                <p className="text-sm text-gray-700">{selectedTheft.notes}</p>
                            </div>
                        )}
                    </div>
                </div>
            ) : (
                <>
                    <div className="mb-4">
                        <p className="text-gray-500">
                            Showing {filteredRecords.length} theft reports for inventory:{" "}
                            <span className="font-medium">{activeInventory?.location || "Unknown"}</span>
                        </p>
                    </div>

                    {filteredRecords.length === 0 ? (
                        <div className="text-center py-8">
                            <AlertTriangle className="h-12 w-12 text-gray-300 mx-auto mb-3" />
                            <p className="text-gray-500">No theft reports found</p>
                            {searchTerm && <p className="text-sm text-gray-400 mt-1">Try adjusting your search</p>}
                        </div>
                    ) : (
                        <div className="space-y-3">
                            {filteredRecords.map((record) => (
                                <div
                                    key={record.id}
                                    className="p-4 border border-gray-200 rounded-md hover:bg-gray-50 cursor-pointer transition-colors"
                                    onClick={() => setSelectedTheft(record)}
                                >
                                    <div className="flex justify-between items-start">
                                        <div>
                                            <h3 className="font-medium text-red-600">{record.productName}</h3>
                                            <p className="text-sm text-gray-500">ID: {record.productId}</p>
                                        </div>
                                        <div className="text-right">
                                            <p className="text-sm font-medium">{record.date}</p>
                                            <p className="text-xs text-gray-500">{record.time}</p>
                                        </div>
                                    </div>
                                    <div className="mt-2 flex justify-between items-center">
                                        <p className="text-sm text-gray-600">{record.location}</p>
                                        <span className="px-2 py-1 bg-red-100 text-red-800 text-xs rounded-full">
                      ${record.value?.toLocaleString()}
                    </span>
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

export default TheftReports

