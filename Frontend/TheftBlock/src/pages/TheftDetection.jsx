// src/pages/TheftDetection.jsx
import React, { useState, useEffect } from 'react';
import { Container, Typography } from '@mui/material';
import { useSelectedInventory } from '../context/SelectedInventoryProvider';
import TheftStatus from '../components/TheftStatus';
import TheftDetailsTable from '../components/TheftDetailsTable';
import RFIDScanLog from '../components/RFIDScanLog';
import { getProductsByInventory, getRFIDScans, detectTheft } from '../services/api';

function TheftDetection() {
  const { selectedInventoryId } = useSelectedInventory();
  const [productsData, setProductsData] = useState({ meta: {}, data: [] });
  const [scanLogsData, setScanLogsData] = useState({ meta: {}, data: [] });
  const [theftOccurrences, setTheftOccurrences] = useState([]);
  const [hasTheft, setHasTheft] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      if (!selectedInventoryId) return;
      setLoading(true);
      setError(null);
      try {
        const productsResponse = await getProductsByInventory(selectedInventoryId);
        const scansResponse = await getRFIDScans(selectedInventoryId);
        const theftData = await detectTheft(productsResponse.data, scansResponse.data);
        console.log('Fetched Products in TheftDetection:', productsResponse); // Debug log
        console.log('Fetched Scans in TheftDetection:', scansResponse); // Debug log
        console.log('Theft Data:', theftData); // Debug log
        setProductsData(productsResponse);
        setScanLogsData(scansResponse);
        setTheftOccurrences(theftData.occurrences);
        setHasTheft(theftData.hasTheft);
      } catch (err) {
        console.error('Error fetching data:', err);
        setError('Failed to fetch data');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [selectedInventoryId]);

  if (loading) return <Typography sx={{ mt: 2, textAlign: 'center' }}>Loading...</Typography>;
  if (error) return <Typography sx={{ mt: 2, textAlign: 'center', color: '#d32f2f' }}>{error}</Typography>;
  if (!selectedInventoryId) return <Typography sx={{ mt: 2, textAlign: 'center' }}>Please select an inventory from the menu.</Typography>;

  return (
    <Container sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" sx={{ mb: 2, fontWeight: 'bold', color: '#333' }}>
        Theft Detection
      </Typography>
      <Typography variant="body2" sx={{ mb: 2, color: '#666' }}>
        Products Last Updated: {productsData.meta.lastUpdated ? new Date(productsData.meta.lastUpdated).toLocaleString() : 'N/A'} | Scans Last Updated: {scanLogsData.meta.lastUpdated ? new Date(scanLogsData.meta.lastUpdated).toLocaleString() : 'N/A'}
      </Typography>
      <TheftStatus hasTheft={hasTheft} affectedProducts={theftOccurrences} />
      {hasTheft && (
        <>
          <Typography variant="h5" sx={{ mt: 3, mb: 1, fontWeight: 'bold', color: '#333' }}>
            Theft Details
          </Typography>
          <TheftDetailsTable theftOccurrences={theftOccurrences || []} />
        </>
      )}
      <Typography variant="h5" sx={{ mt: 3, mb: 1, fontWeight: 'bold', color: '#333' }}>
        RFID Scan Logs
      </Typography>
      <RFIDScanLog scanLogs={scanLogsData.data || []} />
    </Container>
  );
}

export default TheftDetection;