// src/components/DiscrepancyTable.jsx
import React from 'react';
import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper } from '@mui/material';

function DiscrepancyTable({ discrepancies }) {
  return (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell><strong>Date</strong></TableCell>
            <TableCell><strong>Item ID</strong></TableCell>
            <TableCell><strong>Item Name</strong></TableCell>
            <TableCell><strong>Discrepancy</strong></TableCell>
            <TableCell><strong>Financial Loss (₹)</strong></TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {discrepancies.map((d, index) => (
            <TableRow key={index}>
              <TableCell>{d.date}</TableCell>
              <TableCell>{d.itemId}</TableCell>
              <TableCell>{d.itemName}</TableCell>
              <TableCell sx={{ color: 'red' }}>{d.discrepancy}</TableCell>
              <TableCell>{d.loss.toFixed(2)}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}

export default DiscrepancyTable;