// src/components/TheftDetailsTable.jsx
import React from 'react';
import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper } from '@mui/material';

function TheftDetailsTable({ theftOccurrences }) {
  // Debug log to check props
  console.log('TheftDetailsTable theftOccurrences:', theftOccurrences);

  // Ensure theftOccurrences is an array
  const occurrencesList = Array.isArray(theftOccurrences) ? theftOccurrences : [];

  return (
    <TableContainer component={Paper} sx={{ mt: 2, mb: 2 }}>
      <Table sx={{ minWidth: 650 }}>
        <TableHead>
          <TableRow>
            <TableCell sx={{ fontWeight: 'bold' }}>Product ID</TableCell>
            <TableCell sx={{ fontWeight: 'bold' }}>Product Name</TableCell>
            <TableCell sx={{ fontWeight: 'bold' }}>Quantity Missing</TableCell>
            <TableCell sx={{ fontWeight: 'bold' }}>Financial Loss (₹)</TableCell>
            <TableCell sx={{ fontWeight: 'bold' }}>Detected At</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {occurrencesList.length > 0 ? (
            occurrencesList.map((theft, index) => (
              <TableRow key={index}>
                <TableCell>{theft.productId}</TableCell>
                <TableCell>{theft.productName}</TableCell>
                <TableCell sx={{ color: '#d32f2f' }}>{theft.quantityMissing}</TableCell>
                <TableCell>{theft.loss.toFixed(2)}</TableCell>
                <TableCell>{new Date(theft.detectedAt).toLocaleString()}</TableCell>
              </TableRow>
            ))
          ) : (
            <TableRow>
              <TableCell colSpan={5} sx={{ textAlign: 'center' }}>
                No theft occurrences found.
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </TableContainer>
  );
}

export default TheftDetailsTable;