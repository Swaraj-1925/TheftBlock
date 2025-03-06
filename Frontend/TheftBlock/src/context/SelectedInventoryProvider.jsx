// src/context/SelectedInventoryProvider.jsx
import { createContext, useContext, useState } from 'react';

const SelectedInventoryContext = createContext();

export const useSelectedInventory = () => useContext(SelectedInventoryContext);

export const SelectedInventoryProvider = ({ children }) => {
  const [selectedInventoryId, setSelectedInventoryId] = useState(null);

  return (
    <SelectedInventoryContext.Provider value={{ selectedInventoryId, setSelectedInventoryId }}>
      {children}
    </SelectedInventoryContext.Provider>
  );
};