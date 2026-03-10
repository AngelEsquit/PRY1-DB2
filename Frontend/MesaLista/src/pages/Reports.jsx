import { useEffect, useMemo, useState } from "react";
import Navbar from "../components/Navbar";
import {
  fetchPeakHoursReport,
  fetchRestaurants,
  fetchTopDishesReport,
  fetchTopRatedRestaurantsReport,
  fetchSalesByRestaurantReport,
  fetchAvgSpendPerUserReport,
} from "../services/api";

const TABS = [
  { id: "dishes", label: "Platillos mas vendidos" },
  { id: "rated", label: "Mejor calificados" },
  { id: "peak", label: "Horas pico" },
  { id: "sales", label: "Ventas por restaurante" },
  { id: "spend", label: "Gasto promedio" },
];

function Reports() {
  const now = useMemo(() => new Date(), []);
  const [activeTab, setActiveTab] = useState("dishes");
  const [restaurants, setRestaurants] = useState([]);
  const [year, setYear] = useState(now.getFullYear());
  const [month, setMonth] = useState(now.getMonth() + 1);
  const [restaurantId, setRestaurantId] = useState("");
  const [topDishes, setTopDishes] = useState([]);
  const [topRated, setTopRated] = useState([]);
  const [peakHours, setPeakHours] = useState([]);
  const [salesByRest, setSalesByRest] = useState([]);
  const [avgSpend, setAvgSpend] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadRestaurants() {
      try {
        const data = await fetchRestaurants();
        setRestaurants(data);
        if (data.length > 0) setRestaurantId(data[0]._id);
      } catch { setRestaurants([]); }
    }
    loadRestaurants();
  }, []);

  useEffect(() => {
    async function loadReports() {
      if (!restaurantId) return;
      try {
        setLoading(true);
        setError("");
        const [topDishesData, topRatedData, peakHoursData, salesData, spendData] = await Promise.all([
          fetchTopDishesReport({ year, month, restaurantId, limit: 10 }),
          fetchTopRatedRestaurantsReport({ minReviews: 3, limit: 10 }),
          fetchPeakHoursReport(restaurantId),
          fetchSalesByRestaurantReport(),
          fetchAvgSpendPerUserReport(10),
        ]);
        setTopDishes(topDishesData);
        setTopRated(topRatedData);
        setPeakHours(peakHoursData.slice(0, 10));
        setSalesByRest(salesData);
        setAvgSpend(spendData);
      } catch (err) {
        setError(err.message || "No se pudieron cargar los reportes");
      } finally {
        setLoading(false);
      }
    }
    loadReports();
  }, [year, month, restaurantId]);

  return (
    <>
      <Navbar />
      <section className="page-header container">
        <h2>Reportes de Negocio</h2>
        <p>Metricas usando aggregation framework sobre MongoDB.</p>
      </section>
      <section className="container reports-filters">
        <label>Anio
          <input className="form-input" type="number" min={2000} max={2100}
            value={year} onChange={(e) => setYear(Number(e.target.value) || now.getFullYear())} />
        </label>
        <label>Mes
          <select className="form-input" value={month} onChange={(e) => setMonth(Number(e.target.value))}>
            {Array.from({ length: 12 }, (_, i) => i + 1).map((m) => (
              <option key={m} value={m}>{m}</option>
            ))}
          </select>
        </label>
        <label>Restaurante (horas pico y platillos)
          <select className="form-input" value={restaurantId} onChange={(e) => setRestaurantId(e.target.value)}>
            {restaurants.map((r) => <option key={r._id} value={r._id}>{r.nombre}</option>)}
          </select>
        </label>
      </section>
      <section className="container">
        <div className="report-tabs">
          {TABS.map((t) => (
            <button key={t.id}
              className={`report-tab-btn ${activeTab === t.id ? "active" : ""}`}
              onClick={() => setActiveTab(t.id)}>
              {t.label}
            </button>
          ))}
        </div>
      </section>
      <section className="container page-section">
        {loading && <p>Cargando reportes...</p>}
        {error && <p className="error-text">{error}</p>}
        {!loading && !error && (
          <>
            {activeTab === "dishes" && (
              <article className="order-detail-box">
                <h3>Platillos mas vendidos del mes</h3>
                {topDishes.length === 0 && <p>Sin resultados para el periodo seleccionado.</p>}
                {topDishes.map((row, i) => (
                  <p key={i}>{i + 1}. {row.platillo} - {row.cantidad_vendida} vendidos (Q{Number(row.ingresos_generados).toFixed(2)})</p>
                ))}
              </article>
            )}
            {activeTab === "rated" && (
              <article className="order-detail-box">
                <h3>Restaurantes mejor calificados</h3>
                {topRated.length === 0 && <p>No hay suficientes resenas para este ranking.</p>}
                {topRated.map((row, i) => (
                  <p key={i}>{i + 1}. {row.nombre} - {Number(row.promedio_calificacion).toFixed(2)}/5 ({row.total_resenas} resenas)</p>
                ))}
              </article>
            )}
            {activeTab === "peak" && (
              <article className="order-detail-box">
                <h3>Horas pico del restaurante</h3>
                {peakHours.length === 0 && <p>Sin datos para el restaurante seleccionado.</p>}
                {peakHours.map((row, i) => (
                  <p key={i}>{row.dia_semana} {String(row.hora).padStart(2, "0")}:00 - {row.total_ordenes} ordenes</p>
                ))}
              </article>
            )}
            {activeTab === "sales" && (
              <article className="order-detail-box">
                <h3>Ventas por restaurante</h3>
                {salesByRest.length === 0 && <p>Sin datos de ventas.</p>}
                <div className="table-scroll">
                  <table className="admin-table">
                    <thead><tr><th>#</th><th>Restaurante</th><th>Ordenes</th><th>Ventas totales</th><th>Ticket promedio</th></tr></thead>
                    <tbody>
                      {salesByRest.map((row, i) => (
                        <tr key={i}>
                          <td>{i + 1}</td>
                          <td>{row.restaurante || row.restaurante_id}</td>
                          <td>{row.ordenes}</td>
                          <td>Q {Number(row.ventas_totales).toFixed(2)}</td>
                          <td>Q {Number(row.ticket_promedio).toFixed(2)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </article>
            )}
            {activeTab === "spend" && (
              <article className="order-detail-box">
                <h3>Promedio de gasto por usuario (top 10)</h3>
                {avgSpend.length === 0 && <p>Sin datos de gasto.</p>}
                <div className="table-scroll">
                  <table className="admin-table">
                    <thead><tr><th>#</th><th>Usuario</th><th>Email</th><th>Ordenes</th><th>Total gastado</th><th>Promedio</th></tr></thead>
                    <tbody>
                      {avgSpend.map((row, i) => (
                        <tr key={i}>
                          <td>{i + 1}</td>
                          <td>{row.nombre} {row.apellido}</td>
                          <td>{row.email}</td>
                          <td>{row.cantidad_ordenes}</td>
                          <td>Q {Number(row.total_gastado).toFixed(2)}</td>
                          <td>Q {Number(row.promedio_gasto).toFixed(2)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </article>
            )}
          </>
        )}
      </section>
    </>
  );
}

export default Reports;
