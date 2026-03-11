import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import { useCart } from "../context/CartContext";
import { createOrder, fetchUsers } from "../services/api";

function CartPage() {
  const navigate = useNavigate();
  const {
    cartItems,
    removeFromCart,
    increaseQuantity,
    decreaseQuantity,
    clearCart,
    total,
  } = useCart();

  const [usuarioId, setUsuarioId] = useState("");
  const [metodoPago, setMetodoPago] = useState("efectivo");
  const [loading, setLoading] = useState(false);
  const [users, setUsers] = useState([]);

  useEffect(() => {
    async function loadUsers() {
      try {
        const data = await fetchUsers();
        setUsers(data);
      } catch {
        setUsers([]);
      }
    }

    loadUsers();
  }, []);

  useEffect(() => {
    if (!usuarioId && users.length > 0) {
      setUsuarioId(users[0]._id);
    }
  }, [users, usuarioId]);

  const handleConfirmOrder = async () => {
    if (cartItems.length === 0) {
      alert("Tu carrito está vacío");
      return;
    }

    if (!usuarioId.trim()) {
      alert("Debes ingresar el ID del usuario");
      return;
    }

    const restaurantId = cartItems[0]?.restaurantId;

    const hayDistintosRestaurantes = cartItems.some(
      (item) => item.restaurantId !== restaurantId
    );

    if (hayDistintosRestaurantes) {
      alert("Por ahora solo puedes crear una orden con productos de un mismo restaurante");
      return;
    }

    const payload = {
      usuario_id: usuarioId,
      restaurante_id: restaurantId,
      metodo_pago: metodoPago,
      items: cartItems.map((item) => ({
        articulo_id: item.id,
        cantidad: item.quantity,
      })),
    };

    try {
      setLoading(true);
      const response = await createOrder(payload);

      alert(
        `Orden creada con éxito.\nID Orden: ${response.orden_id}\nTotal: Q${response.total}`
      );

      clearCart();
      setUsuarioId("");
      setMetodoPago("efectivo");
    } catch (err) {
      alert(err.message || "No se pudo crear la orden");
    } finally {
      setLoading(false);
    }
  };

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
            <button className="btn btn-primary" onClick={() => navigate("/restaurants")}>
              Ir a restaurantes
            </button>
          </div>
        ) : (
          <>
            <div className="cart-list">
              {cartItems.map((item) => (
                <article key={item.id} className="cart-card">
                  <div>
                    <h3>{item.name}</h3>
                    <p>{item.restaurantName}</p>
                    <p>Q{Number(item.price).toFixed(2)}</p>
                  </div>

                  <div className="cart-controls">
                    <button
                      className="cart-btn"
                      onClick={() => decreaseQuantity(item.id)}
                    >
                      -
                    </button>
                    <span>{item.quantity}</span>
                    <button
                      className="cart-btn"
                      onClick={() => increaseQuantity(item.id)}
                    >
                      +
                    </button>
                  </div>

                  <div>
                    <p className="order-total">
                      Q{(Number(item.price) * item.quantity).toFixed(2)}
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
              <p className="cart-help-text">
                Paso final: verifica usuario, método de pago y luego presiona "Crear Orden".
              </p>

              <label className="cart-label">Usuario</label>
              <select
                className="form-input"
                value={usuarioId}
                onChange={(e) => setUsuarioId(e.target.value)}
              >
                <option value="">Selecciona un usuario</option>
                {users.map((user) => (
                  <option key={user._id} value={user._id}>
                    {user.nombre} {user.apellido} ({user.email})
                  </option>
                ))}
              </select>

              <label className="cart-label">Método de pago</label>
              <select
                className="form-input"
                value={metodoPago}
                onChange={(e) => setMetodoPago(e.target.value)}
              >
                <option value="efectivo">Efectivo</option>
                <option value="tarjeta">Tarjeta</option>
              </select>

              <p>Total de la orden:</p>
              <h2>Q{Number(total).toFixed(2)}</h2>

              <button
                className="btn btn-primary full-width"
                onClick={handleConfirmOrder}
                disabled={loading}
              >
                {loading ? "Creando orden..." : "Crear Orden"}
              </button>
            </div>
          </>
        )}
      </section>
    </>
  );
}

export default CartPage;