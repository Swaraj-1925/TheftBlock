// src/components/SupplierTable.jsx
import React from 'react';
import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper } from '@mui/material';

function SupplierTable({ suppliers }) {
  // Debug log to check props
  console.log('SupplierTable suppliers:', suppliers);

  // Ensure suppliers is an array
  const suppliersList = Array.isArray(suppliers) ? suppliers : [];

  return (
    <TableContainer component={Paper} sx={{ mt: 2, mb: 2 }}>
      <Table sx={{ minWidth: 650 }}>
        <TableHead>
          <TableRow>
            <TableCell sx={{ fontWeight: 'bold' }}>ID</TableCell>
            <TableCell sx={{ fontWeight: 'bold' }}>Name</TableCell>
            <TableCell sx={{ fontWeight: 'bold' }}>Contact</TableCell>
            <TableCell sx={{ fontWeight: 'bold' }}>Address</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {suppliersList.length > 0 ? (
            suppliersList.map((supplier) => (
              <TableRow key={supplier.id}>
                <TableCell>{supplier.id}</TableCell>
                <TableCell>{supplier.name}</TableCell>
                <TableCell>{supplier.contact}</TableCell>
                <TableCell>{supplier.address}</TableCell>
              </TableRow>
            ))
          ) : (
            <TableRow>
              <TableCell colSpan={4} sx={{ textAlign: 'center' }}>
                No suppliers available.
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </TableContainer>
  );
}

export default SupplierTable;