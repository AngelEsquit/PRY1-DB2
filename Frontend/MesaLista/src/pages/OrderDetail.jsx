import { useParams } from "react-router-dom";
import Navbar from "../components/Navbar";
import { orders } from "../data/mockData";

function OrderDetail() {
  const { id } = useParams();
  const order = orders.find((o) => o.id === Number(id));

  if (!order) {
    return (
      <>
        <Navbar />
        <section className="container page-header">
          <h2>Orden no encontrada</h2>
        </section>
      </>
    );
  }

  return (
    <>
      <Navbar />

      <section className="container order-detail-page">
        <h2>Detalle de Orden #{order.id}</h2>

        <div className="order-detail-box">
          <p><strong>Cliente:</strong> {order.customer}</p>
          <p><strong>Restaurante:</strong> {order.restaurant}</p>
          <p><strong>Fecha:</strong> {order.date}</p>
          <p><strong>Estado:</strong> {order.status}</p>

          <div className="order-items">
            <h3>Productos</h3>
            {order.items.map((item, index) => (
              <div key={index} className="order-item-row">
                <span>{item.name} x{item.quantity}</span>
                <span>Q{(item.price * item.quantity).toFixed(2)}</span>
              </div>
            ))}
          </div>

          <h3 className="order-final-total">Total: Q{order.total.toFixed(2)}</h3>
        </div>
      </section>
    </>
  );
}

export default OrderDetail;