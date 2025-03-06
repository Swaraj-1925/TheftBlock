// src/components/TheftStatus.jsx
import React from 'react';
import { Typography } from '@mui/material';

function TheftStatus({ hasTheft, affectedProducts }) {
  return (
    <div>
      <Typography variant="h6" sx={{ mt: 2, mb: 1, fontWeight: 'bold' }}>
        Theft Status
      </Typography>
      {hasTheft ? (
        <Typography variant="h6" sx={{ color: '#d32f2f' }}>
          Theft Detected for {affectedProducts.length} items
        </Typography>
      ) : (
        <Typography variant="h6" sx={{ color: '#388e3c' }}>
          No Theft Detected
        </Typography>
      )}
    </div>
  );
}

export default TheftStatus;