import React, { useState } from 'react';
import {
  Dialog, DialogTitle, DialogContent, DialogActions,
  TextField, Button
} from '@mui/material';

function ReceiveProductsDialog({ open, onClose, onReceive }) {
  const [supplierReceiptId, setSupplierReceiptId] = useState('');

  const handleSubmit = () => {
    onReceive(supplierReceiptId);
    setSupplierReceiptId('');
    onClose();
  };

  return (
    <Dialog open={open} onClose={onClose}>
      <DialogTitle>Receive Products</DialogTitle>
      <DialogContent>
        <TextField
          label="Supplier Receipt ID"
          value={supplierReceiptId}
          onChange={(e) => setSupplierReceiptId(e.target.value)}
          fullWidth
          margin="normal"
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button onClick={handleSubmit} variant="contained">Receive</Button>
      </DialogActions>
    </Dialog>
  );
}

export default ReceiveProductsDialog;