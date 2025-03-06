// src/pages/Dashboard.jsx
import React, { useState, useEffect } from 'react';
import { Container, Typography } from '@mui/material';
import { useSelectedInventory } from '../context/SelectedInventoryProvider';
import KeyMetrics from '../components/KeyMetrics';
import ItemTable from '../components/ItemTable';
import Graphs from '../components/Graphs';
import TheftDetectionSection from '../components/TheftDetectionSection';
import { getProductsByInventory, getRFIDScans } from '../services/api';

function Dashboard() {
  const { selectedInventoryId } = useSelectedInventory();
  const [productsData, setProductsData] = useState({ meta: {}, data: [] });
  const [scanLogsData, setScanLogsData] = useState({ meta: {}, data: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      if (!selectedInventoryId) {
        setLoading(false); // Exit loading state if no inventory is selected
        return;
      }
      setLoading(true);
      setError(null);
      try {
        const productsResponse = await getProductsByInventory(selectedInventoryId);
        const scansResponse = await getRFIDScans(selectedInventoryId);
        console.log('Dashboard - Fetched Products:', productsResponse); // Debug log
        console.log('Dashboard - Fetched Scans:', scansResponse); // Debug log
        setProductsData(productsResponse);
        setScanLogsData(scansResponse);
      } catch (err) {
        console.error('Error fetching data in Dashboard:', err);
        setError('Failed to fetch data');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [selectedInventoryId]);

  console.log('Dashboard - selectedInventoryId:', selectedInventoryId); // Debug log
  console.log('Dashboard - loading:', loading, 'error:', error); // Debug log

  if (loading) return <Typography sx={{ mt: 4, textAlign: 'center', fontSize: '1.5rem', color: '#666' }}>Loading...</Typography>;
  if (error) return <Typography sx={{ mt: 4, textAlign: 'center', fontSize: '1.5rem', color: '#d32f2f' }}>{error}</Typography>;
  if (!selectedInventoryId) return <Typography sx={{ mt: 4, textAlign: 'center', fontSize: '1.5rem', color: '#666' }}>Please select an inventory from the menu.</Typography>;

  return (
    <Container sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" sx={{ mb: 2, fontWeight: 'bold', color: '#333' }}>
        Inventory Dashboard
      </Typography>
      <Typography variant="body2" sx={{ mb: 2, color: '#666' }}>
        Last Updated: {productsData.meta.lastUpdated ? new Date(productsData.meta.lastUpdated).toLocaleString() : 'N/A'}
      </Typography>
      <KeyMetrics products={productsData.data || []} meta={productsData.meta} />
      <Typography variant="h5" sx={{ mt: 3, mb: 1, fontWeight: 'bold', color: '#333' }}>
        Items Overview
      </Typography>
      <ItemTable products={productsData.data || []} />
      <Graphs products={productsData.data || []} />
      <TheftDetectionSection products={productsData.data || []} scanLogs={scanLogsData.data || []} />
    </Container>
  );
}

export default Dashboard;