// src/App.jsx
import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Suppliers from './pages/Suppliers';
import Products from './pages/Products';
import TheftDetection from './pages/TheftDetection';
import { SelectedInventoryProvider } from './context/SelectedInventoryProvider';

function App() {
  return (
    <SelectedInventoryProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Dashboard />} />
            <Route path="suppliers" element={<Suppliers />} />
            <Route path="products" element={<Products />} />
            <Route path="theft-detection" element={<TheftDetection />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </SelectedInventoryProvider>
  );
}

export default App;