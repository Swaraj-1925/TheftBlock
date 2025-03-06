// src/components/AddProductForm.jsx
import React, { useState } from 'react';
import { Grid, TextField, Button } from '@mui/material';
import { addProduct } from '../services/api';

function AddProductForm({ suppliers, onAdd }) {
  const [formData, setFormData] = useState({
    name: '',
    total: '',
    actual_remaining: '',
    price: '',
    rfid: '',
    supplierId: '',
    sold: 0,
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const newProduct = await addProduct({
        ...formData,
        id: `prod${Date.now()}`,
        total: parseInt(formData.total),
        actual_remaining: parseInt(formData.actual_remaining),
        price: parseFloat(formData.price),
        sold: parseInt(formData.sold),
      });
      onAdd(newProduct);
      setFormData({ name: '', total: '', actual_remaining: '', price: '', rfid: '', supplierId: '', sold: 0 });
    } catch (error) {
      console.error('Error adding product:', error);
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <Grid container spacing={2} sx={{ mt: 2, mb: 2 }}>
          <Grid item xs={12} sm={3} sx={{ p: 1 }}>
            <TextField
              label="Name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              fullWidth
              required
              sx={{ '& .MuiInputBase-input': { color: '#333' } }}
            />
          </Grid>
          <Grid item xs={12} sm={3} sx={{ p: 1 }}>
            <TextField
              label="Total Quantity"
              name="total"
              type="number"
              value={formData.total}
              onChange={handleChange}
              fullWidth
              required
              sx={{ '& .MuiInputBase-input': { color: '#333' } }}
            />
          </Grid>
          <Grid item xs={12} sm={3} sx={{ p: 1 }}>
            <TextField
              label="Remaining Quantity"
              name="actual_remaining"
              type="number"
              value={formData.actual_remaining}
              onChange={handleChange}
              fullWidth
              required
              sx={{ '& .MuiInputBase-input': { color: '#333' } }}
            />
          </Grid>
          <Grid item xs={12} sm={3} sx={{ p: 1 }}>
            <TextField
              label="Price (₹)"
              name="price"
              type="number"
              step="0.01"
              value={formData.price}
              onChange={handleChange}
              fullWidth
              required
              sx={{ '& .MuiInputBase-input': { color: '#333' } }}
            />
          </Grid>
          <Grid item xs={12} sm={3} sx={{ p: 1 }}>
            <TextField
              label="RFID"
              name="rfid"
              value={formData.rfid}
              onChange={handleChange}
              fullWidth
              required
              sx={{ '& .MuiInputBase-input': { color: '#333' } }}
            />
          </Grid>
          <Grid item xs={12} sm={3} sx={{ p: 1 }}>
            <TextField
              select
              label="Supplier"
              name="supplierId"
              value={formData.supplierId}
              onChange={handleChange}
              SelectProps={{ native: true }}
              fullWidth
              required
              sx={{ '& .MuiInputBase-input': { color: '#333' } }}
            >
              <option value="">Select Supplier</option>
              {suppliers.map((supplier) => (
                <option key={supplier.id} value={supplier.id}>{supplier.name}</option>
              ))}
            </TextField>
          </Grid>
          <Grid item xs={12} sx={{ p: 1 }}>
            <Button type="submit" variant="contained" sx={{ backgroundColor: '#1976d2', '&:hover': { backgroundColor: '#1565c0' } }}>
              Add Product
            </Button>
          </Grid>
        </Grid>
      </form>
    </div>
  );
}

export default AddProductForm;