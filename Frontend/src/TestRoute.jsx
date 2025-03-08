import { useEffect, useState } from "react";
import fetchAllInventories from "./services/test.jsx"

//For testing only

function TestRoute() {
  const [inventories, setInventories] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    const getInventories = async () => {
      try {
        const data = await fetchAllInventories();
        setInventories(data);
      } catch (err) {
        setError("Failed to fetch inventories.");
      }
    };
    getInventories();
  }, []);

  return (
    <div>
      <h2>Inventories</h2>
      {error && <p style={{ color: "red" }}>{error}</p>}
      <ul>
        {inventories.map((inventory) => (
          <li key={inventory.inventory_id}>
           {inventory.location} - Theft count: {inventory.previous_theft_count}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default TestRoute;
