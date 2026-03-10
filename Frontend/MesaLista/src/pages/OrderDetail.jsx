import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import Navbar from "../components/Navbar";
import { fetchOrderDetail } from "../services/api";

function OrderDetail() {
  const { id } = useParams();
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadOrderDetail() {
      try {
        setLoading(true);
        const data = await fetchOrderDetail(id);
        setOrder(data);
        setError("");
      } catch (err) {
        setError(err.message || "No se pudo cargar la orden");
      } finally {
        setLoading(false);
      }
    }

    loadOrderDetail();
  }, [id]);

  if (loading) {
    return (
      <>
        <Navbar />
        <section className="container page-header">
          <h2>Cargando orden...</h2>
        </section>
      </>
    );
  }

  if (error || !order) {
    return (
      <>
        <Navbar />
        <section className="container page-header">
          <h2>Orden no encontrada</h2>
          {error && <p className="error-text">{error}</p>}
        </section>
      </>
    );
  }

  return (
    <>
      <Navbar />

      <section className="container order-detail-page">
        <h2>Detalle de Orden</h2>

        <div className="order-detail-box">
          <p><strong>ID Orden:</strong> {order._id}</p>
          <p><strong>Usuario:</strong> {order.usuario_nombre || order.usuario_id}</p>
          <p><strong>Restaurante:</strong> {order.restaurante_nombre || order.restaurante_id}</p>
          <p><strong>Fecha:</strong> {order.fecha_pedido ? new Date(order.fecha_pedido).toLocaleString() : "No disponible"}</p>
          <p><strong>Estado:</strong> {order.estado}</p>
          <p><strong>Método de pago:</strong> {order.metodo_pago}</p>

          <div className="order-items">
            <h3>Productos</h3>
            {order.items?.map((item, index) => (
              <div key={index} className="order-item-row">
                <span>{item.nombre} x{item.cantidad}</span>
                <span>Q{item.subtotal}</span>
              </div>
            ))}
          </div>

          <h3 className="order-final-total">Total: Q{order.total}</h3>
        </div>
      </section>
    </>
  );
}

export default OrderDetail;