// src/components/RFIDScanLog.jsx
import React from 'react';
import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper } from '@mui/material';

function RFIDScanLog({ scanLogs }) {
  // Debug log to check props
  console.log('RFIDScanLog scanLogs:', scanLogs);

  // Ensure scanLogs is an array
  const scanLogsList = Array.isArray(scanLogs) ? scanLogs : [];

  return (
    <TableContainer component={Paper} sx={{ mt: 2, mb: 2 }}>
      <Table sx={{ minWidth: 650 }}>
        <TableHead>
          <TableRow>
            <TableCell sx={{ fontWeight: 'bold' }}>Product ID</TableCell>
            <TableCell sx={{ fontWeight: 'bold' }}>Product Name</TableCell>
            <TableCell sx={{ fontWeight: 'bold' }}>Scanned At</TableCell>
            <TableCell sx={{ fontWeight: 'bold' }}>Status</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {scanLogsList.length > 0 ? (
            scanLogsList.map((log, index) => (
              <TableRow key={index}>
                <TableCell>{log.productId}</TableCell>
                <TableCell>{log.productName}</TableCell>
                <TableCell>{new Date(log.scannedAt).toLocaleString()}</TableCell>
                <TableCell sx={{ color: log.status === 'Unsold' ? '#d32f2f' : '#333' }}>
                  {log.status}
                </TableCell>
              </TableRow>
            ))
          ) : (
            <TableRow>
              <TableCell colSpan={4} sx={{ textAlign: 'center' }}>
                No scan logs available.
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </TableContainer>
  );
}

export default RFIDScanLog;