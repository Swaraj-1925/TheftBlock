// src/components/Graphs.jsx
import React from 'react';
import { Bar, Line } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, LineElement, PointElement, Title, Tooltip, Legend } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, LineElement, PointElement, Title, Tooltip, Legend);

function Graphs({ products }) {
  // Debug log to check props
  console.log('Graphs products:', products);

  // Ensure products is an array
  const productsList = Array.isArray(products) ? products : [];

  // Bar Chart: Discrepancies per Item
  const discrepancyData = {
    labels: productsList.map(p => p.name),
    datasets: [
      {
        label: 'Discrepancy (Units Missing)',
        data: productsList.map(p => (p.total - p.sold) - p.actual_remaining),
        backgroundColor: productsList.map(p => ((p.total - p.sold) - p.actual_remaining) > 0 ? 'rgba(255, 99, 132, 0.5)' : 'rgba(75, 192, 192, 0.5)'),
        borderColor: productsList.map(p => ((p.total - p.sold) - p.actual_remaining) > 0 ? 'rgba(255, 99, 132, 1)' : 'rgba(75, 192, 192, 1)'),
        borderWidth: 1,
      },
    ],
  };

  const discrepancyOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { position: 'top' },
      title: { display: true, text: 'Discrepancies per Item' },
      zoom: { pan: { enabled: true }, zoom: { enabled: true } },
    },
    scales: {
      y: { beginAtZero: true },
    },
  };

  // Line Chart: Inventory Levels Over Time (Mock Data)
  const inventoryTrendData = {
    labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
    datasets: [
      {
        label: 'Total Remaining Items',
        data: [productsList.reduce((sum, p) => sum + p.actual_remaining, 0), 250, 240, 230], // Mock trend data
        borderColor: 'rgba(75, 192, 192, 1)',
        backgroundColor: 'rgba(75, 192, 192, 0.5)',
        fill: false,
      },
    ],
  };

  const trendOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { position: 'top' },
      title: { display: true, text: 'Inventory Levels Over Time' },
      zoom: { pan: { enabled: true }, zoom: { enabled: true } },
    },
    scales: {
      y: { beginAtZero: true },
    },
  };

  return (
    <div>
      <Typography variant="h6" sx={{ mt: 2, mb: 1, fontWeight: 'bold' }}>
        Visual Analytics
      </Typography>
      {productsList.length > 0 ? (
        <>
          <div sx={{ mt: 2, mb: 2, width: '100%', height: '400px' }}>
            <Bar data={discrepancyData} options={discrepancyOptions} />
          </div>
          <div sx={{ mt: 2, mb: 2, width: '100%', height: '400px' }}>
            <Line data={inventoryTrendData} options={trendOptions} />
          </div>
        </>
      ) : (
        <Typography sx={{ mt: 2, textAlign: 'center', color: '#666' }}>
          No products available for visualization.
        </Typography>
      )}
    </div>
  );
}

export default Graphs;