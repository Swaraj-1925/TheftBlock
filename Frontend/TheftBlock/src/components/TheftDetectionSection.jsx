// src/components/TheftDetectionSection.jsx
import React from 'react';
import { Typography } from '@mui/material';
import TheftStatus from './TheftStatus';
import TheftDetailsTable from './TheftDetailsTable';
import RFIDScanLog from './RFIDScanLog';

function TheftDetectionSection({ products, scanLogs }) {
  const theftOccurrences = products
    .filter(p => ((p.total - p.sold) - p.actual_remaining) > 0)
    .map(p => ({
      productId: p.id,
      productName: p.name,
      quantityMissing: (p.total - p.sold) - p.actual_remaining,
      loss: ((p.total - p.sold) - p.actual_remaining) * p.price,
      detectedAt: new Date().toISOString(),
    }));

  const hasTheft = theftOccurrences.length > 0;

  return (
    <div>
      <TheftStatus hasTheft={hasTheft} affectedProducts={theftOccurrences} />
      {hasTheft && (
        <>
          <Typography variant="h6" sx={{ mt: 2, mb: 1, fontWeight: 'bold' }}>
            Theft Details
          </Typography>
          <TheftDetailsTable theftOccurrences={theftOccurrences} />
        </>
      )}
      <Typography variant="h6" sx={{ mt: 2, mb: 1, fontWeight: 'bold' }}>
        RFID Scan Logs
      </Typography>
      <RFIDScanLog scanLogs={scanLogs} />
    </div>
  );
}

export default TheftDetectionSection;