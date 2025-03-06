// src/components/Filters.js
import React, { useState } from 'react';
import { Grid, TextField, Button } from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import dayjs from 'dayjs';

function Filters({ onFilterChange, products }) {
  const [dateStart, setDateStart] = useState(null);
  const [dateEnd, setDateEnd] = useState(null);
  const [product, setProduct] = useState('');

  const handleApply = () => {
    onFilterChange({ dateStart, dateEnd, product });
  };

  return (
    <LocalizationProvider dateAdapter={AdapterDayjs}>
      <Grid container spacing={2} alignItems="center">
        <Grid item xs={12} sm={3}>
          <DatePicker
            label="Start Date"
            value={dateStart}
            onChange={(newValue) => setDateStart(newValue)}
            renderInput={(params) => <TextField {...params} fullWidth />}
          />
        </Grid>
        <Grid item xs={12} sm={3}>
          <DatePicker
            label="End Date"
            value={dateEnd}
            onChange={(newValue) => setDateEnd(newValue)}
            renderInput={(params) => <TextField {...params} fullWidth />}
          />
        </Grid>
        <Grid item xs={12} sm={3}>
          <TextField
            select
            label="Product"
            value={product}
            onChange={(e) => setProduct(e.target.value)}
            SelectProps={{ native: true }}
            fullWidth
          >
            <option value="">All</option>
            {products.map((p) => (
              <option key={p.id} value={p.id}>{p.name}</option>
            ))}
          </TextField>
        </Grid>
        <Grid item xs={12} sm={3}>
          <Button variant="contained" onClick={handleApply} fullWidth>
            Apply Filters
          </Button>
        </Grid>
      </Grid>
    </LocalizationProvider>
  );
}

export default Filters;