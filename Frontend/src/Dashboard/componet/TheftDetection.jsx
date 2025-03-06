import React from 'react';
import { Typography } from '@mui/material';

function TheftDetection({ result }) {
  if (!result) return null;
  return (
    <Typography variant="h6" sx={{ mt: 2 }}>
      Discrepancy: {result.discrepancy} items
    </Typography>
  );
}

export default TheftDetection;