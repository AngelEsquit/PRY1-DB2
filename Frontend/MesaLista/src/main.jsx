import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import { CartProvider } from "./context/CartContext";
import { ReviewProvider } from "./context/ReviewContext";
import "./styles/index.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BrowserRouter>
      <ReviewProvider>
        <CartProvider>
          <App />
        </CartProvider>
      </ReviewProvider>
    </BrowserRouter>
  </React.StrictMode>
);