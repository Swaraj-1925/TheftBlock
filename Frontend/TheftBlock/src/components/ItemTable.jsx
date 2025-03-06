// src/components/ItemTable.jsx
import React, { useState, useMemo } from 'react';
import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, TextField, TableSortLabel } from '@mui/material';

function ItemTable({ products }) {
  // Debug log to check props
  console.log('ItemTable products:', products);

  const [search, setSearch] = useState('');
  const [order, setOrder] = useState('asc');
  const [orderBy, setOrderBy] = useState('id');

  // Ensure products is an array
  const productsList = Array.isArray(products) ? products : [];

  const handleRequestSort = (property) => {
    const isAsc = orderBy === property && order === 'asc';
    setOrder(isAsc ? 'desc' : 'asc');
    setOrderBy(property);
  };

  const sortedProducts = useMemo(() => {
    const comparator = (a, b) => {
      const aValue = orderBy === 'discrepancy' ? ((a.total - a.sold) - a.actual_remaining) : a[orderBy];
      const bValue = orderBy === 'discrepancy' ? ((b.total - b.sold) - b.actual_remaining) : b[orderBy];
      if (aValue < bValue) return order === 'asc' ? -1 : 1;
      if (aValue > bValue) return order === 'asc' ? 1 : -1;
      return 0;
    };
    return [...productsList].sort(comparator);
  }, [productsList, order, orderBy]);

  const filteredProducts = sortedProducts.filter((product) =>
    product.name.toLowerCase().includes(search.toLowerCase()) ||
    product.rfid.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <>
      <TextField
        label="Search Items (Name or RFID)"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        fullWidth
        sx={{ mt: 2, mb: 2 }}
      />
      <TableContainer component={Paper} sx={{ mt: 2, mb: 2 }}>
        <Table sx={{ minWidth: 650 }}>
          <TableHead>
            <TableRow>
              <TableCell sx={{ fontWeight: 'bold' }}>
                <TableSortLabel
                  active={orderBy === 'id'}
                  direction={orderBy === 'id' ? order : 'asc'}
                  onClick={() => handleRequestSort('id')}
                >
                  Item ID
                </TableSortLabel>
              </TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>
                <TableSortLabel
                  active={orderBy === 'name'}
                  direction={orderBy === 'name' ? order : 'asc'}
                  onClick={() => handleRequestSort('name')}
                >
                  Item Name
                </TableSortLabel>
              </TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>
                <TableSortLabel
                  active={orderBy === 'rfid'}
                  direction={orderBy === 'rfid' ? order : 'asc'}
                  onClick={() => handleRequestSort('rfid')}
                >
                  RFID
                </TableSortLabel>
              </TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>
                <TableSortLabel
                  active={orderBy === 'total'}
                  direction={orderBy === 'total' ? order : 'asc'}
                  onClick={() => handleRequestSort('total')}
                >
                  Total Quantity
                </TableSortLabel>
              </TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>
                <TableSortLabel
                  active={orderBy === 'sold'}
                  direction={orderBy === 'sold' ? order : 'asc'}
                  onClick={() => handleRequestSort('sold')}
                >
                  Sold Quantity
                </TableSortLabel>
              </TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>
                Expected Remaining
              </TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>
                <TableSortLabel
                  active={orderBy === 'actual_remaining'}
                  direction={orderBy === 'actual_remaining' ? order : 'asc'}
                  onClick={() => handleRequestSort('actual_remaining')}
                >
                  Actual Remaining
                </TableSortLabel>
              </TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>
                <TableSortLabel
                  active={orderBy === 'discrepancy'}
                  direction={orderBy === 'discrepancy' ? order : 'asc'}
                  onClick={() => handleRequestSort('discrepancy')}
                >
                  Discrepancy
                </TableSortLabel>
              </TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>
                <TableSortLabel
                  active={orderBy === 'price'}
                  direction={orderBy === 'price' ? order : 'asc'}
                  onClick={() => handleRequestSort('price')}
                >
                  Price (₹)
                </TableSortLabel>
              </TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>
                Loss (₹)
              </TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredProducts.length > 0 ? (
              filteredProducts.map((product) => {
                const expectedRemaining = product.total - product.sold;
                const discrepancy = expectedRemaining - product.actual_remaining;
                const loss = discrepancy > 0 ? discrepancy * product.price : 0;
                return (
                  <TableRow key={product.id}>
                    <TableCell>{product.id}</TableCell>
                    <TableCell>{product.name}</TableCell>
                    <TableCell>{product.rfid}</TableCell>
                    <TableCell>{product.total}</TableCell>
                    <TableCell>{product.sold}</TableCell>
                    <TableCell>{expectedRemaining}</TableCell>
                    <TableCell>{product.actual_remaining}</TableCell>
                    <TableCell sx={{ color: discrepancy > 0 ? '#d32f2f' : '#333' }}>{discrepancy}</TableCell>
                    <TableCell>{product.price.toFixed(2)}</TableCell>
                    <TableCell sx={{ color: loss > 0 ? '#d32f2f' : '#333' }}>{loss.toFixed(2)}</TableCell>
                  </TableRow>
                );
              })
            ) : (
              <TableRow>
                <TableCell colSpan={10} sx={{ textAlign: 'center' }}>
                  No items available.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </>
  );
}

export default ItemTable;