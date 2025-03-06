// src/components/Layout.jsx
import React from 'react';
import NavigationBar from './NavigationBar';

const Layout = ({ children }) => {
  return (
    <div sx={{ minHeight: '100vh' }}>
      <NavigationBar />
      {children}
    </div>
  );
};

export default Layout;