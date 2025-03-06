// src/components/ProductTable.jsx
import React from 'react';
import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper } from '@mui/material';

function ProductTable({ products }) {
  // Debug log to check props
  console.log('ProductTable products:', products);

  // Ensure products is an array
  const productsList = Array.isArray(products) ? products : [];

  return (
    <TableContainer component={Paper} sx={{ mt: 2, mb: 2 }}>
      <Table sx={{ minWidth: 650 }}>
        <TableHead>
          <TableRow>
            <TableCell sx={{ fontWeight: 'bold' }}>ID</TableCell>
            <TableCell sx={{ fontWeight: 'bold' }}>Name</TableCell>
            <TableCell sx={{ fontWeight: 'bold' }}>Total Quantity</TableCell>
            <TableCell sx={{ fontWeight: 'bold' }}>Remaining Quantity</TableCell>
            <TableCell sx={{ fontWeight: 'bold' }}>Price (₹)</TableCell>
            <TableCell sx={{ fontWeight: 'bold' }}>Supplier ID</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {productsList.length > 0 ? (
            productsList.map((product) => (
              <TableRow key={product.id}>
                <TableCell>{product.id}</TableCell>
                <TableCell>{product.name}</TableCell>
                <TableCell>{product.total}</TableCell>
                <TableCell>{product.actual_remaining}</TableCell>
                <TableCell>{product.price.toFixed(2)}</TableCell>
                <TableCell>{product.supplierId}</TableCell>
              </TableRow>
            ))
          ) : (
            <TableRow>
              <TableCell colSpan={6} sx={{ textAlign: 'center' }}>
                No products available.
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </TableContainer>
  );
}

export default ProductTable;