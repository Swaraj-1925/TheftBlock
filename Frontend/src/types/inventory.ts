export interface InventoryItem {
    id: string
    name: string
    quantity: number
    location: string
    status: string
    price: number
    rfid_tag: string
    supplier_id: string
}

export interface InventoryData {
    totalProducts: number
    onShelf: number
    theftCount: number
    items: InventoryItem[]
}

export interface InventoryStatistics {
    totalProducts: number
    onShelf: number
    theftCount: number
    totalSales: number
    totalSalesValue: number
    estimatedLossValue: number
    totalRacks: number
    totalShelves: number
}

export interface InventoryOwner {
    owner_id: string
    owner_name: string
}

export interface Supplier {
    supplier_id: string
    supplier_name: string
}

export interface StorageRack {
    rack_id: string
    rack_location: string
    shelf_count: number
}

export interface Shelf {
    shelf_id: string
    shelf_location: string
    product_count: number
}

export interface Sale {
    sale_id: string
    product_id: string
    inventory_id: string
    sale_timestamp: string
}

export enum ProductStatus {
    SOLD = "sold",
    ON_SHELF = "on_shelf",
    OUT_SHELF = "out_shelf",
    MISSING = "missing",
    WITH_SUPPLIER = "with_supplier",
}

