// src/components/Sidebar.jsx
import React from 'react';
import { Paper, Typography, Box } from '@mui/material';
import { styled } from '@mui/material/styles';

const StyledSidebar = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(2),
  height: '100%',
  minHeight: '80vh',
}));

const SidebarItem = styled(Box)(({ theme, selected }) => ({
  padding: theme.spacing(1),
  cursor: 'pointer',
  backgroundColor: selected ? theme.palette.grey[200] : 'transparent',
  '&:hover': {
    backgroundColor: theme.palette.grey[100],
  },
}));

function Sidebar({ items, loading, error, onShelfSelect, selectedShelfId }) {
  if (loading) return <StyledSidebar>Loading shelves...</StyledSidebar>;
  if (error) return <StyledSidebar>{error}</StyledSidebar>;

  return (
    <StyledSidebar elevation={3}>
      <Typography variant="h6" gutterBottom>
        Shelves
      </Typography>
      {items.map((item) => (
        <SidebarItem
          key={item.shelf_inventory_id}
          selected={selectedShelfId === item.shelf_inventory_id}
          onClick={() => onShelfSelect(item.shelf_inventory_id)}
        >
          <Typography variant="body1">
            {item.shelf_location} (ID: {item.shelf_inventory_id})
          </Typography>
        </SidebarItem>
      ))}
    </StyledSidebar>
  );
}

export default Sidebar;