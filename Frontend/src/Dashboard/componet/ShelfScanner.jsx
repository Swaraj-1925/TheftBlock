import React from 'react';
import { Button, List, ListItem } from '@mui/material';

function ShelfScanner({ onScan, scanResults }) {
  return (
    <>
      <Button variant="contained" onClick={onScan} sx={{ mb: 2 }}>
        Scan Selected Shelf
      </Button>
      {scanResults.length > 0 && (
        <List sx={{ mb: 2 }}>
          {scanResults.map((rfid, index) => (
            <ListItem key={index}>{rfid}</ListItem>
          ))}
        </List>
      )}
    </>
  );
}

export default ShelfScanner;