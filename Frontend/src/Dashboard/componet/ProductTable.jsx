import React from 'react';
import {
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Button
} from '@mui/material';

function ProductTable({ products, loading, error, onMarkAsSold }) {
  if (loading) return <div>Loading...</div>;
  if (error) return <div>{error}</div>;
  if (products.length === 0) return <div>No products found</div>;

  return (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Product ID</TableCell>
            <TableCell>RFID Tag</TableCell>
            <TableCell>Status</TableCell>
            <TableCell>Action</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {products.map((product) => (
            <TableRow key={product.product_id}>
              <TableCell>{product.product_id}</TableCell>
              <TableCell>{product.rfid_tag}</TableCell>
              <TableCell>{product.status}</TableCell>
              <TableCell>
                <Button
                  variant="contained"
                  color="primary"
                  onClick={() => onMarkAsSold(product.rfid_tag)}
                  disabled={product.status !== 'available'}
                >
                  Mark as Sold
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}

export default ProductTable;