import { useEffect, useState } from "react";
import Navbar from "../components/Navbar";
import { fetchOrders } from "../services/api";
import { useNavigate } from "react-router-dom";

function Orders() {
  const navigate = useNavigate();
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadOrders() {
      try {
        setLoading(true);
        const data = await fetchOrders();
        setOrders(data);
        setError("");
      } catch (err) {
        setError(err.message || "No se pudieron cargar las órdenes");
      } finally {
        setLoading(false);
      }
    }

    loadOrders();
  }, []);

  return (
    <>
      <Navbar />

      <section className="page-header container">
        <h2>Órdenes</h2>
        <p>Consulta el historial y estado de tus pedidos.</p>
      </section>

      <section className="container orders-list page-section">
        {loading && <p>Cargando órdenes...</p>}
        {error && <p className="error-text">{error}</p>}

        {!loading &&
          !error &&
          orders.map((order) => (
            <article key={order._id} className="order-card">
              <div>
                <h3>Restaurante: {order.restaurante_nombre || order.restaurante_id}</h3>
                <p>Cliente: {order.usuario_nombre || order.usuario_id}</p>
                <p>
                  Fecha:{" "}
                  {order.fecha_pedido
                    ? new Date(order.fecha_pedido).toLocaleDateString()
                    : "No disponible"}
                </p>
              </div>

              <div>
                <p className="order-status">{order.estado}</p>
                <p className="order-total">Q{order.total}</p>
              </div>

              <button
                className="btn btn-accent"
                onClick={() => navigate(`/orders/${order._id}`)}
              >
                Ver Detalle
              </button>
            </article>
          ))}
      </section>
    </>
  );
}

export default Orders;