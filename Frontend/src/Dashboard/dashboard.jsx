import React, { useState, useEffect } from 'react';
import {
  Container, Grid, Button, Dialog, DialogTitle, DialogContent, DialogActions,
  TextField, List, ListItem, Typography
} from '@mui/material';
import axios from 'axios';
import ProductTable from './componet/ProductTable.jsx';
import CardItem from './componet/CardItem.jsx';
import Sidebar from './componet/Sidebar.jsx';
import ReceiveProductsDialog from "./componet/ReceiveProductsDialog.jsx";
import MetricsCards from "./componet/MetricsCards.jsx";
import ShelfScanner from "./componet/ShelfScanner.jsx";
import InventoryActions from "./componet/InventoryActions.jsx";
import TheftDetection from "./componet/TheftDetection.jsx";
import CreateSupplierDialog from "./componet/CreateSupplierDialog.jsx";

function Dashboard() {
  const [shelfItems, setShelfItems] = useState([]);
  const [products, setProducts] = useState([]);
  const [metrics, setMetrics] = useState({
    totalReceived: 0,
    totalSold: 0,
    totalInventory: 0,
    missingItems: 0,
  });
  const [selectedShelfId, setSelectedShelfId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [scanResults, setScanResults] = useState([]);
  const [theftDetectionResult, setTheftDetectionResult] = useState(null);
  const [openCreateSupplierDialog, setOpenCreateSupplierDialog] = useState(false);
  const [openReceiveProductsDialog, setOpenReceiveProductsDialog] = useState(false);

  const API_BASE_URL = 'http://localhost:8000';

  // Fetch initial data
  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        console.log("Sending POST to:", `${API_BASE_URL}/api/supplier/create`);
        const shelfResponse = await axios.get(`${API_BASE_URL}/api/shelf-inventory`);
        setShelfItems(shelfResponse.data);
        console.log("Shelf data:", shelfResponse.data);

        const metricsResponse = await axios.get(`${API_BASE_URL}/api/metrics`);
        setMetrics(metricsResponse.data);
        if (shelfResponse.data.length > 0) {
          setSelectedShelfId(shelfResponse.data[0].shelf_inventory_id);
        }
        setLoading(false);
      } catch (err) {
        console.error("Error:", err);
    console.error("Response data:", err.response.data);
    setError('Failed to create supplier');
      }
    };
    fetchInitialData();
  }, []);

  // Fetch products for selected shelf
  useEffect(() => {
    const fetchProductsForShelf = async () => {
      if (!selectedShelfId) return;
      setLoading(true);
      try {
        const response = await axios.get(`${API_BASE_URL}/api/shelf-inventory/${selectedShelfId}/products`);
        setProducts(response.data);
        setLoading(false);
      } catch (err) {
        setError('Failed to fetch products');
        setLoading(false);
      }
    };
    fetchProductsForShelf();
  }, [selectedShelfId]);

  // Fetch theft detection
  useEffect(() => {
    const fetchTheftDetection = async () => {
      if (!selectedShelfId) return;
      try {
        const response = await axios.get(`${API_BASE_URL}/api/theft/warehouse_to_consumer/${selectedShelfId}`);
        setTheftDetectionResult(response.data);
      } catch (err) {
        setError('Failed to fetch theft detection');
      }
    };
    fetchTheftDetection();
  }, [selectedShelfId]);

  // Dialog handlers
  const handleOpenCreateSupplierDialog = () => setOpenCreateSupplierDialog(true);
  const handleCloseCreateSupplierDialog = () => setOpenCreateSupplierDialog(false);
  const handleOpenReceiveProductsDialog = () => setOpenReceiveProductsDialog(true);
  const handleCloseReceiveProductsDialog = () => setOpenReceiveProductsDialog(false);

  // API handlers
  const handleCreateSupplier = async (data) => {
    try {
      await axios.post(`${API_BASE_URL}/api/supplier/create`, data);
      const shelfResponse = await axios.get(`${API_BASE_URL}/api/shelf-inventory`);
      setShelfItems(shelfResponse.data);
      handleCloseCreateSupplierDialog();
    } catch (err) {
      setError('Failed to create supplier');
    }
  };

  const handleReceiveProducts = async (supplierReceiptId) => {
    try {
      await axios.post(`${API_BASE_URL}/api/warehouse/receive/${supplierReceiptId}`);
      const metricsResponse = await axios.get(`${API_BASE_URL}/api/metrics`);
      setMetrics(metricsResponse.data);
      if (selectedShelfId) {
        const productResponse = await axios.get(`${API_BASE_URL}/api/shelf-inventory/${selectedShelfId}/products`);
        setProducts(productResponse.data);
      }
      handleCloseReceiveProductsDialog();
    } catch (err) {
      setError('Failed to receive products');
    }
  };

  const handleMarkAsSold = async (rfidTag) => {
    try {
      await axios.post(`${API_BASE_URL}/api/product/mark-sold/${rfidTag}`);
      const productResponse = await axios.get(`${API_BASE_URL}/api/shelf-inventory/${selectedShelfId}/products`);
      setProducts(productResponse.data);
      const metricsResponse = await axios.get(`${API_BASE_URL}/api/metrics`);
      setMetrics(metricsResponse.data);
    } catch (err) {
      setError('Failed to mark product as sold');
    }
  };

  const handleScanShelf = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/shelf/scan/${selectedShelfId}`);
      setScanResults(response.data);
    } catch (err) {
      setError('Failed to scan shelf');
    }
  };

  const handleShelfSelect = (shelfId) => {
    setSelectedShelfId(shelfId);
    setScanResults([]);
  };

  if (loading && !selectedShelfId) return <Container>Loading...</Container>;
  if (error) return <Container>{error}</Container>;

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Grid container spacing={3}>
        {/* Sidebar */}
        <Grid item xs={12} md={3}>
          <Sidebar
            items={shelfItems}
            loading={loading && !shelfItems.length}
            error={error}
            onShelfSelect={handleShelfSelect}
            selectedShelfId={selectedShelfId}
          />
        </Grid>

        {/* Main Content */}
        <Grid item xs={12} md={9}>
          <InventoryActions
            onOpenCreateSupplier={handleOpenCreateSupplierDialog}
            onOpenReceiveProducts={handleOpenReceiveProductsDialog}
          />
          <MetricsCards metrics={metrics} />
          <ShelfScanner onScan={handleScanShelf} scanResults={scanResults} />
          <ProductTable
            products={products}
            loading={loading}
            error={error}
            onMarkAsSold={handleMarkAsSold}
          />
          <TheftDetection result={theftDetectionResult} />
        </Grid>
      </Grid>

      <CreateSupplierDialog
        open={openCreateSupplierDialog}
        onClose={handleCloseCreateSupplierDialog}
        onCreate={handleCreateSupplier}
      />
      <ReceiveProductsDialog
        open={openReceiveProductsDialog}
        onClose={handleCloseReceiveProductsDialog}
        onReceive={handleReceiveProducts}
      />
    </Container>
  );
}

export default Dashboard;