// src/pages/Suppliers.jsx
import React, { useState, useEffect } from 'react';
import { Container, Typography } from '@mui/material';
import SupplierTable from '../components/SupplierTable';
import AddSupplierForm from '../components/AddSupplierForm';
import { getSuppliers } from '../services/api';

function Suppliers() {
  const [suppliersData, setSuppliersData] = useState({ meta: {}, data: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchSuppliers = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await getSuppliers();
        setSuppliersData(data);
      } catch (err) {
        setError('Failed to fetch suppliers');
      } finally {
        setLoading(false);
      }
    };
    fetchSuppliers();
  }, []);

  const handleAddSupplier = (newSupplier) => {
    setSuppliersData((prev) => ({
      meta: { ...prev.meta, lastUpdated: new Date().toISOString(), totalSuppliers: prev.data.length + 1 },
      data: [...prev.data, newSupplier],
    }));
  };

  if (loading) return <Typography sx={{ mt: 2, textAlign: 'center' }}>Loading...</Typography>;
  if (error) return <Typography sx={{ mt: 2, textAlign: 'center', color: '#d32f2f' }}>{error}</Typography>;

  return (
    <Container sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" sx={{ mb: 2, fontWeight: 'bold', color: '#333' }}>
        Suppliers
      </Typography>
      <Typography variant="body2" sx={{ mb: 2, color: '#666' }}>
        Last Updated: {suppliersData.meta.lastUpdated ? new Date(suppliersData.meta.lastUpdated).toLocaleString() : 'N/A'}
      </Typography>
      <AddSupplierForm onAdd={handleAddSupplier} />
      <SupplierTable suppliers={suppliersData.data} />
    </Container>
  );
}

export default Suppliers;