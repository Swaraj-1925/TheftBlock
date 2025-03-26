import axios from "axios";
const API_BASE_URL = "/api";


//for testing only
export const fetchAllInventories = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/inventory`);
    console.log(response)
    return response.data;
  } catch (error) {
    console.error("Error fetching inventories:", error);
    throw error;
  }
};
export default fetchAllInventories;
