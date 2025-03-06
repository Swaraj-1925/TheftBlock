// src/services/api.jsx
// Sample data with metadata
let inventories = {
  meta: {
    lastUpdated: new Date().toISOString(),
    source: "Sample Data",
    totalInventories: 2,
  },
  data: [
    { id: "inv1", name: "Inventory 1" },
    { id: "inv2", name: "Inventory 2" },
  ],
};

let suppliers = {
  meta: {
    lastUpdated: new Date().toISOString(),
    source: "Sample Data",
    totalSuppliers: 2,
  },
  data: [
    { id: "sup1", name: "Supplier A", contact: "123-456-7890", address: "123 Main St" },
    { id: "sup2", name: "Supplier B", contact: "098-765-4321", address: "456 Elm St" },
  ],
};

let products = {
  meta: {
    lastUpdated: new Date().toISOString(),
    source: "Sample Data",
    totalProducts: 4,
  },
  data: [
    {
      id: "prod1",
      name: "Pen",
      total: 100,
      actual_remaining: 80,
      price: 10,
      rfid: "RFID001",
      supplierId: "sup1",
      inventoryId: "inv1",
      sold: 15,
    },
    {
      id: "prod2",
      name: "Pencil",
      total: 200,
      actual_remaining: 180,
      price: 5,
      rfid: "RFID002",
      supplierId: "sup1",
      inventoryId: "inv1",
      sold: 20,
    },
    {
      id: "prod3",
      name: "Notebook",
      total: 150,
      actual_remaining: 140,
      price: 50,
      rfid: "RFID003",
      supplierId: "sup2",
      inventoryId: "inv2",
      sold: 10,
    },
    {
      id: "prod4",
      name: "Eraser",
      total: 300,
      actual_remaining: 250,
      price: 2,
      rfid: "RFID004",
      supplierId: "sup2",
      inventoryId: "inv2",
      sold: 50,
    },
  ],
};

let rfidScans = {
  meta: {
    lastUpdated: new Date().toISOString(),
    source: "Sample Data",
    totalScans: 4,
  },
  data: [
    { productId: "prod1", productName: "Pen", scannedAt: "2025-03-05T12:00:00Z", status: "Unsold", inventoryId: "inv1" },
    { productId: "prod2", productName: "Pencil", scannedAt: "2025-03-05T12:05:00Z", status: "Sold", inventoryId: "inv1" },
    { productId: "prod3", productName: "Notebook", scannedAt: "2025-03-05T12:10:00Z", status: "Sold", inventoryId: "inv2" },
    { productId: "prod4", productName: "Eraser", scannedAt: "2025-03-05T12:15:00Z", status: "Unsold", inventoryId: "inv2" },
  ],
};

// Functions returning sample data
export const getInventories = async () => {
  return inventories.data;
};

export const getSuppliers = async () => {
  return suppliers; // Return the full object with meta and data
};

export const addSupplier = async (supplier) => {
  suppliers.data.push(supplier);
  suppliers.meta.lastUpdated = new Date().toISOString();
  suppliers.meta.totalSuppliers = suppliers.data.length;
  return supplier;
};

export const getProducts = async () => {
  return products; // Return the full object with meta and data
};

export const addProduct = async (product) => {
  products.data.push(product);
  products.meta.lastUpdated = new Date().toISOString();
  products.meta.totalProducts = products.data.length;
  return product;
};

export const getProductsByInventory = async (inventoryId) => {
  const filteredProducts = products.data.filter(p => p.inventoryId === inventoryId);
  return {
    meta: products.meta,
    data: filteredProducts,
  };
};

export const getRFIDScans = async (inventoryId) => {
  const filteredScans = rfidScans.data.filter(s => s.inventoryId === inventoryId);
  return {
    meta: rfidScans.meta,
    data: filteredScans,
  };
};

export const detectTheft = async (productsData, scanLogsData) => {
  const theftOccurrences = [];
  scanLogsData.forEach((log) => {
    if (log.status === 'Unsold') {
      const product = productsData.find((p) => p.id === log.productId);
      if (product) {
        const discrepancy = (product.total - product.sold) - product.actual_remaining;
        if (discrepancy > 0) {
          theftOccurrences.push({
            productId: log.productId,
            productName: product.name,
            quantityMissing: discrepancy,
            loss: discrepancy * product.price,
            detectedAt: new Date().toISOString(),
          });
        }
      }
    }
  });
  const hasTheft = theftOccurrences.length > 0;
  return { hasTheft, occurrences: theftOccurrences };
};