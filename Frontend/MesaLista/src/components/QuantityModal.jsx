import { useState } from "react";
import { useCart } from "../context/CartContext";

function QuantityModal({ isOpen, onClose, restaurant, item }) {
  const { addToCart } = useCart();
  const [quantity, setQuantity] = useState(1);

  if (!isOpen || !item || !restaurant) return null;

  const handleConfirm = () => {
    addToCart(restaurant, item, quantity);
    setQuantity(1);
    onClose();
  };

  return (
    <div className="modal-overlay">
      <div className="quantity-modal">
        <button className="modal-close" onClick={onClose}>
          ×
        </button>

        <img src={item.image} alt={item.name} className="modal-image" />

        <h3>{item.name}</h3>
        <p>{item.description}</p>
        <p className="menu-price">Q{item.price.toFixed(2)}</p>

        <div className="modal-quantity-box">
          <button
            className="cart-btn"
            onClick={() => setQuantity((prev) => Math.max(1, prev - 1))}
          >
            -
          </button>

          <span className="modal-quantity">{quantity}</span>

          <button
            className="cart-btn"
            onClick={() => setQuantity((prev) => prev + 1)}
          >
            +
          </button>
        </div>

        <button className="btn btn-accent full-width" onClick={handleConfirm}>
          Agregar al carrito
        </button>
      </div>
    </div>
  );
}

export default QuantityModal;