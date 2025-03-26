import { BrowserRouter as Router, Routes, Route } from "react-router-dom"
import Layout from "./components/Layout"
import InventoryDashboard from "./pages/InventoryDashboard"
import ProductDetails from "./pages/ProductDetails"
import TheftReports from "./pages/TheftReports"
import NotFound from "./pages/NotFound"

function App() {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<Layout />}>
                    <Route index ="/inventory" element={<InventoryDashboard />} />
                    <Route path="product/:productId" element={<ProductDetails />} />
                    <Route path="thefts" element={<TheftReports />} />
                    <Route path="*" element={<NotFound />} />
                </Route>
            </Routes>
        </Router>
    )
}

export default App

