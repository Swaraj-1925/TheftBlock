import React, { useState } from 'react';
import {
  Dialog, DialogTitle, DialogContent, DialogActions,
  TextField, Button
} from '@mui/material';

function CreateSupplierDialog({ open, onClose, onCreate }) {
  const [supplierId, setSupplierId] = useState('');
  const [supplierName, setSupplierName] = useState('');
  const [productCount, setProductCount] = useState(0);

  const handleSubmit = () => {
    onCreate({ supplier_id: supplierId, supplier_name: supplierName, product_count: productCount });
    setSupplierId('');
    setSupplierName('');
    setProductCount(0);
    onClose();
  };

  return (
    <Dialog open={open} onClose={onClose}>
      <DialogTitle>Create Supplier and Products</DialogTitle>
      <DialogContent>
        <TextField
          label="Supplier ID"
          value={supplierId}
          onChange={(e) => setSupplierId(e.target.value)}
          fullWidth
          margin="normal"
        />
        <TextField
          label="Supplier Name"
          value={supplierName}
          onChange={(e) => setSupplierName(e.target.value)}
          fullWidth
          margin="normal"
        />
        <TextField
          label="Product Count"
          type="number"
          value={productCount}
          onChange={(e) => setProductCount(parseInt(e.target.value) || 0)}
          fullWidth
          margin="normal"
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button onClick={handleSubmit} variant="contained">Create</Button>
      </DialogActions>
    </Dialog>
  );
}

export default CreateSupplierDialog;