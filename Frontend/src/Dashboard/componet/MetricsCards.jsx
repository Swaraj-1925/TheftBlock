import React from 'react';
import { Grid } from '@mui/material';
import CardItem from './CardItem';

function MetricsCards({ metrics }) {
  const cardData = [
    { title: 'Total Items Received', value: metrics.totalReceived },
    { title: 'Total Items Sold', value: metrics.totalSold },
    { title: 'Total Items in Inventory', value: metrics.totalInventory },
    { title: 'Missing Items', value: metrics.missingItems },
  ];

  return (
    <Grid container spacing={3} sx={{ mb: 4 }}>
      {cardData.map((card, index) => (
        <Grid item xs={12} sm={6} md={3} key={index}>
          <CardItem title={card.title} value={card.value} />
        </Grid>
      ))}
    </Grid>
  );
}

export default MetricsCards;