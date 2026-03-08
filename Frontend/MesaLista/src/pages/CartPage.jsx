import Navbar from "../components/Navbar";
import { useCart } from "../context/CartContext";

function CartPage() {
  const {
    cartItems,
    removeFromCart,
    increaseQuantity,
    decreaseQuantity,
    clearCart,
    total,
  } = useCart();

  return (
    <>
      <Navbar />

      <section className="container page-header">
        <h2>Carrito</h2>
        <p>Revisa tus productos antes de confirmar la orden.</p>
      </section>

      <section className="container cart-page">
        {cartItems.length === 0 ? (
          <div className="empty-cart">
            <h3>Tu carrito está vacío</h3>
            <p>Agrega productos desde el detalle del restaurante.</p>
          </div>
        ) : (
          <>
            <div className="cart-list">
              {cartItems.map((item) => (
                <article key={item.id} className="cart-card">
                  <div>
                    <h3>{item.name}</h3>
                    <p>{item.restaurantName}</p>
                    <p>Q{item.price.toFixed(2)}</p>
                  </div>

                  <div className="cart-controls">
                    <button className="cart-btn" onClick={() => decreaseQuantity(item.id)}>
                      -
                    </button>
                    <span>{item.quantity}</span>
                    <button className="cart-btn" onClick={() => increaseQuantity(item.id)}>
                      +
                    </button>
                  </div>

                  <div>
                    <p className="order-total">
                      Q{(item.price * item.quantity).toFixed(2)}
                    </p>
                    <button
                      className="btn btn-light"
                      onClick={() => removeFromCart(item.id)}
                    >
                      Eliminar
                    </button>
                  </div>
                </article>
              ))}
            </div>

            <div className="cart-summary">
              <h3>Resumen</h3>
              <p>Total de la orden:</p>
              <h2>Q{total.toFixed(2)}</h2>

              <button
                className="btn btn-primary full-width"
                onClick={() => {
                  alert("Orden creada con éxito");
                  clearCart();
                }}
              >
                Confirmar Orden
              </button>
            </div>
          </>
        )}
      </section>
    </>
  );
}

export default CartPage;