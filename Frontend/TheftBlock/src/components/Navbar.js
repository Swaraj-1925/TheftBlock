// src/components/Navbar.js
import React from 'react';
import { AppBar, Toolbar, Typography } from '@mui/material';

function Navbar() {
  return (
    <AppBar position="static" color="primary">
      <Toolbar>
        <Typography variant="h6">Inventory Theft Detection Dashboard</Typography>
      </Toolbar>
    </AppBar>
  );
}

export default Navbar;