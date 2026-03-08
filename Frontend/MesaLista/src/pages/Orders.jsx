import Navbar from "../components/Navbar";
import { orders } from "../data/mockData";
import { useNavigate } from "react-router-dom";

function Orders() {
  const navigate = useNavigate();

  return (
    <>
      <Navbar />

      <section className="page-header container">
        <h2>Órdenes</h2>
        <p>Consulta el historial y estado de tus pedidos.</p>
      </section>

      <section className="container orders-list page-section">
        {orders.map((order) => (
          <article key={order.id} className="order-card">
            <div>
              <h3>{order.restaurant}</h3>
              <p>Fecha: {order.date}</p>
            </div>

            <div>
              <p className="order-status">{order.status}</p>
              <p className="order-total">Q{order.total.toFixed(2)}</p>
            </div>

            <button
              className="btn btn-accent"
              onClick={() => navigate(`/orders/${order.id}`)}
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