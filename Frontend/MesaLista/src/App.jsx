import { Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import Restaurants from "./pages/Restaurants";
import RestaurantDetail from "./pages/RestaurantDetail";
import Orders from "./pages/Orders";
import OrderDetail from "./pages/OrderDetail";
import Reviews from "./pages/Reviews";
import CartPage from "./pages/CartPage";
import Reports from "./pages/Reports";
import Admin from "./pages/Admin";
import Arrays from "./pages/Arrays";
import Transactions from "./pages/Transactions";
import GridFS from "./pages/GridFS";
import Indices from "./pages/Indices";

function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/restaurants" element={<Restaurants />} />
      <Route path="/restaurants/:id" element={<RestaurantDetail />} />
      <Route path="/orders" element={<Orders />} />
      <Route path="/orders/:id" element={<OrderDetail />} />
      <Route path="/reviews" element={<Reviews />} />
      <Route path="/reports" element={<Reports />} />
      <Route path="/cart" element={<CartPage />} />
      <Route path="/admin" element={<Admin />} />
      <Route path="/arrays" element={<Arrays />} />
      <Route path="/transactions" element={<Transactions />} />
      <Route path="/gridfs" element={<GridFS />} />
      <Route path="/indices" element={<Indices />} />
    </Routes>
  );
}

export default App;