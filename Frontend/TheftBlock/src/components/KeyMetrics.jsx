// src/components/KeyMetrics.jsx
import React from 'react';
import { Grid, Paper, Typography } from '@mui/material';

function KeyMetrics({ products, meta }) {
  const totalItems = products.length;
  const remainingItems = products.reduce((sum, p) => sum + p.actual_remaining, 0);
  const soldItems = products.reduce((sum, p) => sum + p.sold, 0);
  const discrepancies = products.reduce((count, p) => ((p.total - p.sold) - p.actual_remaining) > 0 ? count + 1 : count, 0);
  const financialLoss = products.reduce(
    (sum, p) => ((p.total - p.sold) - p.actual_remaining) > 0 ? sum + (((p.total - p.sold) - p.actual_remaining) * p.price) : sum,
    0
  );

  return (
    <Grid container spacing={2} sx={{ mt: 2, mb: 2 }}>
      <Grid item xs={12} sm={4} md={2.4}>
        <Paper sx={{ p: 2, textAlign: 'center', backgroundColor: '#f5f5f5', borderRadius: 2, boxShadow: 3 }}>
          <Typography variant="h6" sx={{ color: '#333' }}>Total Items</Typography>
          <Typography variant="h4" sx={{ color: '#1976d2' }}>{totalItems}</Typography>
          <Typography variant="body2" sx={{ color: '#666', mt: 1 }}>
            Total in Data: {meta.totalProducts || 'N/A'}
          </Typography>
        </Paper>
      </Grid>
      <Grid item xs={12} sm={4} md={2.4}>
        <Paper sx={{ p: 2, textAlign: 'center', backgroundColor: '#f5f5f5', borderRadius: 2, boxShadow: 3 }}>
          <Typography variant="h6" sx={{ color: '#333' }}>Remaining Items</Typography>
          <Typography variant="h4" sx={{ color: '#1976d2' }}>{remainingItems}</Typography>
        </Paper>
      </Grid>
      <Grid item xs={12} sm={4} md={2.4}>
        <Paper sx={{ p: 2, textAlign: 'center', backgroundColor: '#f5f5f5', borderRadius: 2, boxShadow: 3 }}>
          <Typography variant="h6" sx={{ color: '#333' }}>Sold Items</Typography>
          <Typography variant="h4" sx={{ color: '#1976d2' }}>{soldItems}</Typography>
        </Paper>
      </Grid>
      <Grid item xs={12} sm={4} md={2.4}>
        <Paper sx={{ p: 2, textAlign: 'center', backgroundColor: '#f5f5f5', borderRadius: 2, boxShadow: 3 }}>
          <Typography variant="h6" sx={{ color: '#333' }}>Discrepancies</Typography>
          <Typography variant="h4" sx={{ color: discrepancies > 0 ? '#d32f2f' : '#388e3c' }}>{discrepancies}</Typography>
        </Paper>
      </Grid>
      <Grid item xs={12} sm={4} md={2.4}>
        <Paper sx={{ p: 2, textAlign: 'center', backgroundColor: '#f5f5f5', borderRadius: 2, boxShadow: 3 }}>
          <Typography variant="h6" sx={{ color: '#333' }}>Financial Loss (₹)</Typography>
          <Typography variant="h4" sx={{ color: financialLoss > 0 ? '#d32f2f' : '#388e3c' }}>{financialLoss.toFixed(2)}</Typography>
        </Paper>
      </Grid>
    </Grid>
  );
}

export default KeyMetrics;