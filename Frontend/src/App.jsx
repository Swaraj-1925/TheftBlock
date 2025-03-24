import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import TestRoute from "./TestRoute";

function Dummy() {
  return <h2>Dummy</h2>;
}

function App() {
  return (

     //For testing only
    <Router>
      <Routes>
        <Route path="/" element={<Dummy />} />
        <Route path="/inventory" element={<TestRoute />} />
      </Routes>
    </Router>
  );
}

export default App;
