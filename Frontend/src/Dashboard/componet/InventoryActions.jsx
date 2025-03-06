import React from 'react';
import { Grid, Button } from '@mui/material';

function InventoryActions({ onOpenCreateSupplier, onOpenReceiveProducts }) {
  return (
    <Grid container spacing={2} sx={{ mb: 2 }}>
      <Grid item>
        <Button variant="contained" onClick={onOpenCreateSupplier}>
          Create Supplier
        </Button>
      </Grid>
      <Grid item>
        <Button variant="contained" onClick={onOpenReceiveProducts}>
          Receive Products
        </Button>
      </Grid>
    </Grid>
  );
}

export default InventoryActions;