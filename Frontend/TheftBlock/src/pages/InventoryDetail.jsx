// src/pages/InventoryDetail.jsx
import React, { useState, useEffect } from 'react';
import { Container, Typography, Button } from '@mui/material';
import { useParams, useNavigate } from 'react-router-dom';
import Summary from '../components/Summary';
import ItemTable from '../components/ItemTable';
import Filters from '../components/Filters';
import InventoryChart from '../components/InventoryChart';
import DiscrepancyTable from '../components/DiscrepancyTable';
import { getInventoryById, getChartData } from '../services/api';
import dayjs from 'dayjs';

function InventoryDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [inventory, setInventory] = useState(null);
  const [filteredDiscrepancies, setFilteredDiscrepancies] = useState([]);
  const [chartData, setChartData] = useState({ dates: [], losses: [] });
  const [filters, setFilters] = useState({ dateStart: null, dateEnd: null, product: '' });

  useEffect(() => {
    const inv = getInventoryById(id);
    if (inv) {
      setInventory(inv);
      setFilteredDiscrepancies(inv.discrepancies);
      setChartData(getChartData(inv.discrepancies));
    }
  }, [id]);

  const handleFilterChange = (newFilters) => {
    setFilters(newFilters);
    let filtered = [...inventory.discrepancies];
    if (newFilters.dateStart) {
      filtered = filtered.filter((d) => dayjs(d.date).isAfter(dayjs(newFilters.dateStart).subtract(1, 'day')));
    }
    if (newFilters.dateEnd) {
      filtered = filtered.filter((d) => dayjs(d.date).isBefore(dayjs(newFilters.dateEnd).add(1, 'day')));
    }
    if (newFilters.product) {
      filtered = filtered.filter((d) => d.itemId === newFilters.product);
    }
    setFilteredDiscrepancies(filtered);
    setChartData(getChartData(filtered));
  };

  if (!inventory) return <Typography>Loading...</Typography>;

  const totalDiscrepancies = filteredDiscrepancies.reduce((sum, d) => sum + Math.abs(d.discrepancy), 0);
  const totalLoss = filteredDiscrepancies.reduce((sum, d) => sum + d.loss, 0);

  return (
    <Container sx={{ mt: 4, mb: 4 }}>
      <Button variant="outlined" onClick={() => navigate('/')} sx={{ mb: 2 }}>
        Back to Inventory List
      </Button>
      <Typography variant="h5" gutterBottom>
        {inventory.name} - Overview
      </Typography>
      <Summary totalDiscrepancies={totalDiscrepancies} totalLoss={totalLoss} />
      
      <Typography variant="h6" gutterBottom sx={{ mt: 4 }}>
        Inventory Items
      </Typography>
      <ItemTable items={inventory.items} />
      
      <Typography variant="h6" gutterBottom sx={{ mt: 4 }}>
        Filters
      </Typography>
      <Filters onFilterChange={handleFilterChange} products={inventory.items} />
      
      <Typography variant="h6" gutterBottom sx={{ mt: 4 }}>
        Discrepancy Trends
      </Typography>
      <InventoryChart chartData={chartData} />
      
      <Typography variant="h6" gutterBottom sx={{ mt: 4 }}>
        Discrepancy Details
      </Typography>
      <DiscrepancyTable discrepancies={filteredDiscrepancies} />
    </Container>
  );
}

export default InventoryDetail;