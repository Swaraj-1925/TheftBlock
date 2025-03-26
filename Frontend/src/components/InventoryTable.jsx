"use client"

import { useState } from "react"
import { MoreHorizontal, ArrowUpDown, Check, X, AlertTriangle } from "lucide-react"
import { ProductStatus } from "../constants/productStatus"

const InventoryTable = ({ items, loading, onSelectProduct }) => {
    const [sortField, setSortField] = useState("name")
    const [sortDirection, setSortDirection] = useState("asc")
    const [selectedRow, setSelectedRow] = useState(null)

    const handleSort = (field) => {
        if (sortField === field) {
            setSortDirection(sortDirection === "asc" ? "desc" : "asc")
        } else {
            setSortField(field)
            setSortDirection("asc")
        }
    }

    const handleRowClick = (item) => {
        if (loading) return

        setSelectedRow(item.id)
        if (onSelectProduct) {
            onSelectProduct(item)
        }
    }

    const sortedItems = [...items].sort((a, b) => {
        if (a[sortField] < b[sortField]) return sortDirection === "asc" ? -1 : 1
        if (a[sortField] > b[sortField]) return sortDirection === "asc" ? 1 : -1
        return 0
    })

    // Generate placeholder rows for loading state or empty data
    const placeholderRows = Array(10)
        .fill(null)
        .map((_, index) => ({
            id: `placeholder-${index}`,
            name: "Bold text column",
            quantity: 1,
            location: "Regular text column",
            status: "Regular text column",
            price: 0,
            rfid_tag: "Regular text column",
            supplier_id: "Regular text column",
        }))

    const displayItems = loading || items.length === 0 ? placeholderRows : sortedItems

    const getStatusIcon = (status) => {
        switch (status) {
            case ProductStatus.ON_SHELF:
                return <Check className="h-4 w-4 text-green-500" />
            case ProductStatus.SOLD:
                return <Check className="h-4 w-4 text-blue-500" />
            case ProductStatus.MISSING:
                return <AlertTriangle className="h-4 w-4 text-red-500" />
            case ProductStatus.OUT_SHELF:
                return <X className="h-4 w-4 text-orange-500" />
            default:
                return null
        }
    }

    const getStatusText = (status) => {
        switch (status) {
            case ProductStatus.ON_SHELF:
                return "On Shelf"
            case ProductStatus.SOLD:
                return "Sold"
            case ProductStatus.MISSING:
                return "Missing"
            case ProductStatus.OUT_SHELF:
                return "Out of Shelf"
            case ProductStatus.WITH_SUPPLIER:
                return "With Supplier"
            default:
                return status
        }
    }

    return (
        <div className="overflow-x-auto">
            <table className="min-w-full">
                <thead>
                <tr>
                    <th
                        className="px-4 py-2 text-left text-sm font-medium text-gray-500 border-b cursor-pointer"
                        onClick={() => handleSort("name")}
                    >
                        <div className="flex items-center">
                            Product Name
                            <ArrowUpDown className="ml-1 h-4 w-4" />
                        </div>
                    </th>
                    <th
                        className="px-4 py-2 text-left text-sm font-medium text-gray-500 border-b cursor-pointer"
                        onClick={() => handleSort("id")}
                    >
                        <div className="flex items-center">
                            ID
                            <ArrowUpDown className="ml-1 h-4 w-4" />
                        </div>
                    </th>
                    <th
                        className="px-4 py-2 text-left text-sm font-medium text-gray-500 border-b cursor-pointer"
                        onClick={() => handleSort("price")}
                    >
                        <div className="flex items-center">
                            Price
                            <ArrowUpDown className="ml-1 h-4 w-4" />
                        </div>
                    </th>
                    <th
                        className="px-4 py-2 text-left text-sm font-medium text-gray-500 border-b cursor-pointer"
                        onClick={() => handleSort("location")}
                    >
                        <div className="flex items-center">
                            Location
                            <ArrowUpDown className="ml-1 h-4 w-4" />
                        </div>
                    </th>
                    <th
                        className="px-4 py-2 text-left text-sm font-medium text-gray-500 border-b cursor-pointer"
                        onClick={() => handleSort("status")}
                    >
                        <div className="flex items-center">
                            Status
                            <ArrowUpDown className="ml-1 h-4 w-4" />
                        </div>
                    </th>
                    <th className="px-4 py-2 text-left text-sm font-medium text-gray-500 border-b"></th>
                </tr>
                </thead>
                <tbody>
                {displayItems.map((item, index) => (
                    <tr
                        key={item.id}
                        className={`${index % 2 === 0 ? "bg-white" : "bg-gray-50"} ${
                            selectedRow === item.id ? "bg-blue-50" : ""
                        } ${!loading ? "cursor-pointer hover:bg-blue-50" : ""}`}
                        onClick={() => handleRowClick(item)}
                    >
                        <td className="px-4 py-3 font-semibold">{item.name}</td>
                        <td className="px-4 py-3 text-gray-500">{item.id}</td>
                        <td className="px-4 py-3 text-gray-500">${loading ? "-" : item.price.toLocaleString()}</td>
                        <td className="px-4 py-3 text-gray-500">{item.location}</td>
                        <td className="px-4 py-3 text-gray-500">
                            <div className="flex items-center">
                                {!loading && getStatusIcon(item.status)}
                                <span className="ml-1">{loading ? item.status : getStatusText(item.status)}</span>
                            </div>
                        </td>
                        <td className="px-4 py-3 text-gray-400">
                            <MoreHorizontal className="h-5 w-5" />
                        </td>
                    </tr>
                ))}
                </tbody>
            </table>
        </div>
    )
}

export default InventoryTable

