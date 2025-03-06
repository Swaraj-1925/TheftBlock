// src/components/NavigationBar.jsx
import React, { useState, useEffect } from 'react';
import { AppBar, Toolbar, Typography, IconButton, Drawer, List, ListItem, ListItemText } from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import { getInventories } from '../services/api';
import { useSelectedInventory } from '../context/SelectedInventoryProvider';

function NavigationBar() {
  const [open, setOpen] = useState(false);
  const [inventories, setInventories] = useState([]);
  const { selectedInventoryId, setSelectedInventoryId } = useSelectedInventory();

  useEffect(() => {
    const fetchInventories = async () => {
      try {
        const data = await getInventories();
        console.log('Fetched Inventories in NavigationBar:', data); // Debug log
        // Ensure data is an array
        const inventoryList = Array.isArray(data) ? data : [];
        setInventories(inventoryList);
        // Set default inventory if none is selected
        if (inventoryList.length > 0 && !selectedInventoryId) {
          setSelectedInventoryId(inventoryList[0].id);
          console.log('Set default inventory ID:', inventoryList[0].id); // Debug log
        }
      } catch (err) {
        console.error('Error fetching inventories:', err);
        setInventories([]);
      }
    };
    fetchInventories();
  }, [setSelectedInventoryId, selectedInventoryId]);

  const toggleDrawer = () => {
    setOpen(!open);
  };

  const handleInventorySelect = (id) => {
    setSelectedInventoryId(id);
    console.log('Selected inventory ID:', id); // Debug log
    setOpen(false);
  };

  return (
    <>
      <AppBar position="static" sx={{ backgroundColor: '#1976d2', boxShadow: 3 }}>
        <Toolbar>
          <IconButton edge="start" color="inherit" onClick={toggleDrawer} sx={{ mr: 2 }}>
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" sx={{ flexGrow: 1, fontWeight: 'bold' }}>
            TheftBlock Dashboard
          </Typography>
        </Toolbar>
      </AppBar>
      <Drawer anchor="left" open={open} onClose={toggleDrawer} sx={{ '.MuiDrawer-paper': { width: 250, backgroundColor: '#f5f5f5' } }}>
        <List>
          {inventories.length > 0 ? (
            inventories.map((inventory) => (
              <ListItem
                button
                key={inventory.id}
                onClick={() => handleInventorySelect(inventory.id)}
                sx={{ '&:hover': { backgroundColor: '#e0e0e0' } }}
              >
                <ListItemText primary={inventory.name} sx={{ color: '#333' }} />
              </ListItem>
            ))
          ) : (
            <ListItem>
              <ListItemText primary="No inventories available" sx={{ color: '#666' }} />
            </ListItem>
          )}
        </List>
      </Drawer>
    </>
  );
}

export default NavigationBar;