// src/components/Summary.js
import React from 'react';
import { Grid, Card, CardContent, Typography } from '@mui/material';

function Summary({ totalDiscrepancies, totalLoss }) {
  return (
    <Grid container spacing={2}>
      <Grid item xs={12} sm={6}>
        <Card>
          <CardContent>
            <Typography variant="h6">Total Discrepancies</Typography>
            <Typography variant="h4" color="error">
              {totalDiscrepancies}
            </Typography>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} sm={6}>
        <Card>
          <CardContent>
            <Typography variant="h6">Estimated Financial Loss</Typography>
            <Typography variant="h4" color="error">
              ₹{totalLoss.toFixed(2)}
            </Typography>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
}

export default Summary;