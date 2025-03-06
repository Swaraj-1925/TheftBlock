// src/components/RemainingProductsTable.jsx
import React from 'react';
import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper } from '@mui/material';

function RemainingProductsTable({ products }) {
  // Debug log to check props
  console.log('RemainingProductsTable products:', products);

  // Ensure products is an array
  const productsList = Array.isArray(products) ? products : [];

  return (
    <TableContainer component={Paper} sx={{ mt: 2, mb: 2 }}>
      <Table sx={{ minWidth: 650 }}>
        <TableHead>
          <TableRow>
            <TableCell sx={{ fontWeight: 'bold' }}>Product ID</TableCell>
            <TableCell sx={{ fontWeight: 'bold' }}>Name</TableCell>
            <TableCell sx={{ fontWeight: 'bold' }}>Remaining Quantity</TableCell>
            <TableCell sx={{ fontWeight: 'bold' }}>Supplier ID</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {productsList.length > 0 ? (
            productsList.map((product) => (
              <TableRow key={product.id}>
                <TableCell>{product.id}</TableCell>
                <TableCell>{product.name}</TableCell>
                <TableCell>{product.actual_remaining}</TableCell>
                <TableCell>{product.supplierId}</TableCell>
              </TableRow>
            ))
          ) : (
            <TableRow>
              <TableCell colSpan={4} sx={{ textAlign: 'center' }}>
                No remaining products available.
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </TableContainer>
  );
}

export default RemainingProductsTable;