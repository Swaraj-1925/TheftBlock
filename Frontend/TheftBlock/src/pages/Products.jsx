// src/pages/Products.jsx
import React, { useState, useEffect } from 'react';
import { Container, Typography } from '@mui/material';
import ProductTable from '../components/ProductTable';
import AddProductForm from '../components/AddProductForm';
import RemainingProductsTable from '../components/RemainingProductsTable';
import { getSuppliers, getProducts } from '../services/api';

function Products() {
  const [suppliersData, setSuppliersData] = useState({ meta: {}, data: [] });
  const [productsData, setProductsData] = useState({ meta: {}, data: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const suppliers = await getSuppliers();
        const products = await getProducts();
        setSuppliersData(suppliers);
        setProductsData(products);
      } catch (err) {
        setError('Failed to fetch data');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleAddProduct = (newProduct) => {
    setProductsData((prev) => ({
      meta: { ...prev.meta, lastUpdated: new Date().toISOString(), totalProducts: prev.data.length + 1 },
      data: [...prev.data, newProduct],
    }));
  };

  if (loading) return <Typography sx={{ mt: 2, textAlign: 'center' }}>Loading...</Typography>;
  if (error) return <Typography sx={{ mt: 2, textAlign: 'center', color: '#d32f2f' }}>{error}</Typography>;

  return (
    <Container sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" sx={{ mb: 2, fontWeight: 'bold', color: '#333' }}>
        Products
      </Typography>
      <Typography variant="body2" sx={{ mb: 2, color: '#666' }}>
        Last Updated: {productsData.meta.lastUpdated ? new Date(productsData.meta.lastUpdated).toLocaleString() : 'N/A'}
      </Typography>
      <AddProductForm suppliers={suppliersData.data} onAdd={handleAddProduct} />
      <Typography variant="h5" sx={{ mt: 3, mb: 1, fontWeight: 'bold', color: '#333' }}>
        All Products
      </Typography>
      <ProductTable products={productsData.data} />
      <Typography variant="h5" sx={{ mt: 3, mb: 1, fontWeight: 'bold', color: '#333' }}>
        Remaining Products
      </Typography>
      <RemainingProductsTable products={productsData.data} />
    </Container>
  );
}

export default Products;