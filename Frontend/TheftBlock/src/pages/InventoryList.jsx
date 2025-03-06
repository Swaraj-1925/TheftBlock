// src/pages/InventoryList.jsx
import React, { useState, useEffect } from 'react';
import { Container, Typography, Grid } from '@mui/material';
import InventoryCard from '../components/InventoryCard';
import { getInventories } from '../services/api';

function InventoryList() {
  const [inventories, setInventories] = useState([]);

  useEffect(() => {
    setInventories(getInventories());
  }, []);

  return (
    <Container sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h5" gutterBottom>
        Inventory List
      </Typography>
      <Grid container spacing={2}>
        {inventories.map((inventory) => (
          <Grid item xs={12} sm={6} md={4} key={inventory.id}>
            <InventoryCard inventory={inventory} />
          </Grid>
        ))}
      </Grid>
    </Container>
  );
}

export default InventoryList;