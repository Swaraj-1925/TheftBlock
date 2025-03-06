// src/components/AddSupplierForm.jsx
import React, { useState } from 'react';
import { Grid, TextField, Button } from '@mui/material';
import { addSupplier } from '../services/api';

function AddSupplierForm({ onAdd }) {
  const [formData, setFormData] = useState({
    name: '',
    contact: '',
    address: '',
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const newSupplier = await addSupplier({
        ...formData,
        id: `sup${Date.now()}`,
      });
      onAdd(newSupplier);
      setFormData({ name: '', contact: '', address: '' });
    } catch (error) {
      console.error('Error adding supplier:', error);
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <Grid container spacing={2} sx={{ mt: 2, mb: 2 }}>
          <Grid item xs={12} sm={4} sx={{ p: 1 }}>
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
          <Grid item xs={12} sm={4} sx={{ p: 1 }}>
            <TextField
              label="Contact"
              name="contact"
              value={formData.contact}
              onChange={handleChange}
              fullWidth
              required
              sx={{ '& .MuiInputBase-input': { color: '#333' } }}
            />
          </Grid>
          <Grid item xs={12} sm={4} sx={{ p: 1 }}>
            <TextField
              label="Address"
              name="address"
              value={formData.address}
              onChange={handleChange}
              fullWidth
              required
              sx={{ '& .MuiInputBase-input': { color: '#333' } }}
            />
          </Grid>
          <Grid item xs={12} sx={{ p: 1 }}>
            <Button type="submit" variant="contained" sx={{ backgroundColor: '#1976d2', '&:hover': { backgroundColor: '#1565c0' } }}>
              Add Supplier
            </Button>
          </Grid>
        </Grid>
      </form>
    </div>
  );
}

export default AddSupplierForm;