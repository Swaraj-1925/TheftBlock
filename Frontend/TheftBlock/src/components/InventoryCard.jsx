// src/components/InventoryCard.jsx
import React from 'react';
import { Card, CardContent, Typography, Button } from '@mui/material';
import { useNavigate } from 'react-router-dom';

function InventoryCard({ inventory }) {
  const navigate = useNavigate();
  const totalDiscrepancies = inventory.discrepancies.reduce((sum, d) => sum + Math.abs(d.discrepancy), 0);
  const totalLoss = inventory.discrepancies.reduce((sum, d) => sum + d.loss, 0);

  return (
    <Card sx={{ mb: 2 }}>
      <CardContent>
        <Typography variant="h6">{inventory.name}</Typography>
        <Typography>Total Items: {inventory.items.reduce((sum, i) => sum + i.total, 0)}</Typography>
        <Typography color="error">Discrepancies: {totalDiscrepancies}</Typography>
        <Typography color="error">Loss: ₹{totalLoss.toFixed(2)}</Typography>
        <Button
          variant="contained"
          sx={{ mt: 1 }}
          onClick={() => navigate(`/inventory/${inventory.id}`)}
        >
          View Details
        </Button>
      </CardContent>
    </Card>
  );
}

export default InventoryCard;