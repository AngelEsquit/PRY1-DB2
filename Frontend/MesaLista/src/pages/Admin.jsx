import { useState } from "react";
import {
  fetchUsers,
  fetchRestaurants,
  fetchOrders,
  fetchReviews,
  createUser,
  createRestaurant,
  createMenuItem,
  updateUserEmail,
  updateRestaurantPhone,
  updateMenuItemPrice,
  updateOrderStatus,
  deleteUser,
  deleteRestaurant,
  deleteMenuItem,
  deleteReview,
  deactivateInactiveUsers,
  applyCategoryDiscount,
  markOldOrders,
  cleanOldReviews,
  cleanInactiveUsers,
  cleanCancelledOrders,
} from "../services/api";

const ORDER_STATES = ["pendiente", "confirmado", "preparando", "en_camino", "entregado", "cancelado"];

function ResultBox({ result }) {
  if (!result) return null;
  const isError = result.type === "error";
  return (
    <div className={`result-box ${isError ? "result-error" : "result-ok"}`}>
      <pre>{typeof result.data === "string" ? result.data : JSON.stringify(result.data, null, 2)}</pre>
    </div>
  );
}

// ── CREATE TAB ───────────────────────────────────────────────────
function CreateTab() {
  const [active, setActive] = useState("user");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  // User form state
  const [user, setUser] = useState({ nombre: "", apellido: "", email: "", telefono: "", ciudad: "Guatemala" });
  // Restaurant form state
  const [rest, setRest] = useState({ nombre: "", descripcion: "", tipo_comida: "", telefono: "", email: "", ciudad: "Guatemala" });
  // Menu item form state
  const [item, setItem] = useState({ restaurante_id: "", nombre: "", descripcion: "", categoria: "", precio: "", ingredientes: "", opciones_personalizacion: "", tiempo_preparacion: "15" });

  const run = async (fn) => {
    setLoading(true);
    setResult(null);
    try {
      const data = await fn();
      setResult({ type: "ok", data });
    } catch (e) {
      setResult({ type: "error", data: e.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="admin-section">
      <div className="admin-subtabs">
        {["user", "restaurant", "menuitem"].map((t) => (
          <button key={t} className={`subtab-btn ${active === t ? "active" : ""}`} onClick={() => { setActive(t); setResult(null); }}>
            {t === "user" ? "Usuario" : t === "restaurant" ? "Restaurante" : "Artículo de menú"}
          </button>
        ))}
      </div>

      {active === "user" && (
        <form className="admin-form" onSubmit={(e) => { e.preventDefault(); run(() => createUser(user)); }}>
          <h3>Crear usuario</h3>
          {[["nombre","Nombre"],["apellido","Apellido"],["email","Email"],["telefono","Teléfono"],["ciudad","Ciudad"]].map(([k,l]) => (
            <label key={k}>{l}<input value={user[k]} onChange={e => setUser(p => ({...p, [k]: e.target.value}))} required={k !== "ciudad"} /></label>
          ))}
          <button type="submit" disabled={loading} className="btn-primary">{loading ? "Creando…" : "Crear usuario"}</button>
        </form>
      )}

      {active === "restaurant" && (
        <form className="admin-form" onSubmit={(e) => { e.preventDefault(); run(() => createRestaurant({ ...rest, tipo_comida: rest.tipo_comida.split(",").map(s => s.trim()).filter(Boolean) })); }}>
          <h3>Crear restaurante</h3>
          {[["nombre","Nombre"],["descripcion","Descripción"],["tipo_comida","Tipos de comida (separados por coma)"],["telefono","Teléfono"],["email","Email"],["ciudad","Ciudad"]].map(([k,l]) => (
            <label key={k}>{l}<input value={rest[k]} onChange={e => setRest(p => ({...p, [k]: e.target.value}))} required={k !== "ciudad"} /></label>
          ))}
          <button type="submit" disabled={loading} className="btn-primary">{loading ? "Creando…" : "Crear restaurante"}</button>
        </form>
      )}

      {active === "menuitem" && (
        <form className="admin-form" onSubmit={(e) => {
          e.preventDefault();
          run(() => createMenuItem(item.restaurante_id, {
            nombre: item.nombre,
            descripcion: item.descripcion,
            categoria: item.categoria,
            precio: parseFloat(item.precio),
            ingredientes: item.ingredientes.split(",").map(s => s.trim()).filter(Boolean),
            opciones_personalizacion: item.opciones_personalizacion.split(",").map(s => s.trim()).filter(Boolean),
            tiempo_preparacion: parseInt(item.tiempo_preparacion),
          }));
        }}>
          <h3>Crear artículo de menú</h3>
          {[
            ["restaurante_id","ID del restaurante"],
            ["nombre","Nombre"],
            ["descripcion","Descripción"],
            ["categoria","Categoría"],
            ["precio","Precio (GTQ)"],
            ["ingredientes","Ingredientes (separados por coma)"],
            ["opciones_personalizacion","Opciones (separadas por coma)"],
            ["tiempo_preparacion","Tiempo de preparación (min)"],
          ].map(([k,l]) => (
            <label key={k}>{l}<input value={item[k]} onChange={e => setItem(p => ({...p, [k]: e.target.value}))} required={k !== "opciones_personalizacion"} type={["precio","tiempo_preparacion"].includes(k) ? "number" : "text"} min={k === "precio" ? "0.01" : k === "tiempo_preparacion" ? "1" : undefined} step={k === "precio" ? "0.01" : undefined} /></label>
          ))}
          <button type="submit" disabled={loading} className="btn-primary">{loading ? "Creando…" : "Crear artículo"}</button>
        </form>
      )}

      <ResultBox result={result} />
    </div>
  );
}

// ── READ TAB ─────────────────────────────────────────────────────
function ReadTab() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({ userTipo: "", orderStatus: "" });

  const load = async (fn) => {
    setLoading(true);
    setError(null);
    setData(null);
    try {
      setData(await fn());
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="admin-section">
      <h3>Consultar colecciones</h3>
      <div className="read-actions">
        <div className="read-action-group">
          <label>Usuarios
            <select value={filters.userTipo} onChange={e => setFilters(p => ({...p, userTipo: e.target.value}))}>
              <option value="">Todos</option>
              <option value="regular">Regular</option>
              <option value="premium">Premium</option>
              <option value="admin">Admin</option>
            </select>
          </label>
          <button className="btn-secondary" onClick={() => load(() => fetchUsers(filters.userTipo || undefined))}>Ver usuarios</button>
        </div>

        <div className="read-action-group">
          <button className="btn-secondary" onClick={() => load(fetchRestaurants)}>Ver restaurantes</button>
        </div>

        <div className="read-action-group">
          <label>Órdenes por estado
            <select value={filters.orderStatus} onChange={e => setFilters(p => ({...p, orderStatus: e.target.value}))}>
              <option value="">Todas</option>
              {ORDER_STATES.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
          </label>
          <button className="btn-secondary" onClick={() => load(fetchOrders)}>Ver órdenes</button>
        </div>

        <div className="read-action-group">
          <button className="btn-secondary" onClick={() => load(fetchReviews)}>Ver reseñas</button>
        </div>
      </div>

      {loading && <p className="loading-text">Cargando…</p>}
      {error && <div className="result-box result-error"><pre>{error}</pre></div>}
      {data && (
        <div className="read-results">
          <p className="results-count">{data.length} resultado(s)</p>
          <div className="table-scroll">
            <table className="admin-table">
              <thead>
                <tr>{Object.keys(data[0] || {}).slice(0, 6).map(k => <th key={k}>{k}</th>)}</tr>
              </thead>
              <tbody>
                {data.slice(0, 50).map((row, i) => (
                  <tr key={i}>
                    {Object.values(row).slice(0, 6).map((v, j) => (
                      <td key={j}>{typeof v === "object" ? JSON.stringify(v) : String(v ?? "")}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

// ── UPDATE TAB ───────────────────────────────────────────────────
function UpdateTab() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [fields, setFields] = useState({
    userId: "", newEmail: "",
    restId: "", newPhone: "",
    orderId: "", newStatus: ORDER_STATES[0],
    itemId: "", newPrice: "",
    inactiveMonths: "6",
    discountCat: "", discountPct: "",
  });

  const set = (k) => (e) => setFields(p => ({ ...p, [k]: e.target.value }));

  const run = async (fn) => {
    setLoading(true);
    setResult(null);
    try {
      setResult({ type: "ok", data: await fn() });
    } catch (e) {
      setResult({ type: "error", data: e.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="admin-section">
      <div className="update-grid">
        {/* User email */}
        <div className="update-card">
          <h4>Actualizar email de usuario</h4>
          <input placeholder="ID usuario" value={fields.userId} onChange={set("userId")} />
          <input placeholder="Nuevo email" value={fields.newEmail} onChange={set("newEmail")} />
          <button className="btn-primary" disabled={loading} onClick={() => run(() => updateUserEmail(fields.userId, fields.newEmail))}>Actualizar</button>
        </div>

        {/* Restaurant phone */}
        <div className="update-card">
          <h4>Actualizar teléfono de restaurante</h4>
          <input placeholder="ID restaurante" value={fields.restId} onChange={set("restId")} />
          <input placeholder="Nuevo teléfono" value={fields.newPhone} onChange={set("newPhone")} />
          <button className="btn-primary" disabled={loading} onClick={() => run(() => updateRestaurantPhone(fields.restId, fields.newPhone))}>Actualizar</button>
        </div>

        {/* Order status */}
        <div className="update-card">
          <h4>Cambiar estado de orden</h4>
          <input placeholder="ID orden" value={fields.orderId} onChange={set("orderId")} />
          <select value={fields.newStatus} onChange={set("newStatus")}>
            {ORDER_STATES.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
          <button className="btn-primary" disabled={loading} onClick={() => run(() => updateOrderStatus(fields.orderId, fields.newStatus))}>Actualizar</button>
        </div>

        {/* Menu item price */}
        <div className="update-card">
          <h4>Actualizar precio de artículo</h4>
          <input placeholder="ID artículo" value={fields.itemId} onChange={set("itemId")} />
          <input placeholder="Nuevo precio" type="number" min="0.01" step="0.01" value={fields.newPrice} onChange={set("newPrice")} />
          <button className="btn-primary" disabled={loading} onClick={() => run(() => updateMenuItemPrice(fields.itemId, parseFloat(fields.newPrice)))}>Actualizar</button>
        </div>

        {/* Bulk: deactivate inactive users */}
        <div className="update-card">
          <h4>Desactivar usuarios inactivos (masivo)</h4>
          <label>Meses de inactividad
            <input type="number" min="1" max="60" value={fields.inactiveMonths} onChange={set("inactiveMonths")} />
          </label>
          <button className="btn-warning" disabled={loading} onClick={() => run(() => deactivateInactiveUsers(parseInt(fields.inactiveMonths)))}>Desactivar</button>
        </div>

        {/* Bulk: category discount */}
        <div className="update-card">
          <h4>Aplicar descuento por categoría (masivo)</h4>
          <input placeholder="Categoría (ej: Bebidas)" value={fields.discountCat} onChange={set("discountCat")} />
          <input placeholder="% descuento (ej: 10)" type="number" min="1" max="99" value={fields.discountPct} onChange={set("discountPct")} />
          <button className="btn-warning" disabled={loading} onClick={() => run(() => applyCategoryDiscount(fields.discountCat, parseFloat(fields.discountPct)))}>Aplicar</button>
        </div>

        {/* Bulk: mark old orders */}
        <div className="update-card">
          <h4>Marcar órdenes anticuadas (masivo)</h4>
          <p className="card-note">Órdenes de más de un año con estado ciertas serán marcadas como archivadas.</p>
          <button className="btn-warning" disabled={loading} onClick={() => run(markOldOrders)}>Marcar</button>
        </div>
      </div>

      <ResultBox result={result} />
    </div>
  );
}

// ── DELETE TAB ───────────────────────────────────────────────────
function DeleteTab() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [fields, setFields] = useState({ userId: "", restId: "", itemId: "", reviewId: "", oldReviewYears: "2" });

  const set = (k) => (e) => setFields(p => ({ ...p, [k]: e.target.value }));

  const run = async (fn) => {
    setLoading(true);
    setResult(null);
    try {
      setResult({ type: "ok", data: await fn() });
    } catch (e) {
      setResult({ type: "error", data: e.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="admin-section">
      <div className="update-grid">
        <div className="update-card">
          <h4>Eliminar usuario</h4>
          <p className="card-note">Falla si el usuario tiene órdenes o reseñas.</p>
          <input placeholder="ID usuario" value={fields.userId} onChange={set("userId")} />
          <button className="btn-danger" disabled={loading} onClick={() => run(() => deleteUser(fields.userId))}>Eliminar</button>
        </div>

        <div className="update-card">
          <h4>Eliminar restaurante</h4>
          <input placeholder="ID restaurante" value={fields.restId} onChange={set("restId")} />
          <button className="btn-danger" disabled={loading} onClick={() => run(() => deleteRestaurant(fields.restId))}>Eliminar</button>
        </div>

        <div className="update-card">
          <h4>Eliminar artículo de menú</h4>
          <p className="card-note">Falla si el artículo está en órdenes activas.</p>
          <input placeholder="ID artículo" value={fields.itemId} onChange={set("itemId")} />
          <button className="btn-danger" disabled={loading} onClick={() => run(() => deleteMenuItem(fields.itemId))}>Eliminar</button>
        </div>

        <div className="update-card">
          <h4>Eliminar reseña</h4>
          <input placeholder="ID reseña" value={fields.reviewId} onChange={set("reviewId")} />
          <button className="btn-danger" disabled={loading} onClick={() => run(() => deleteReview(fields.reviewId))}>Eliminar</button>
        </div>

        <div className="update-card">
          <h4>Limpiar reseñas antiguas (masivo)</h4>
          <label>Años de antigüedad
            <input type="number" min="1" max="20" value={fields.oldReviewYears} onChange={set("oldReviewYears")} />
          </label>
          <button className="btn-danger" disabled={loading} onClick={() => run(() => cleanOldReviews(parseInt(fields.oldReviewYears)))}>Limpiar</button>
        </div>

        <div className="update-card">
          <h4>Eliminar usuarios inactivos (masivo)</h4>
          <p className="card-note">Elimina usuarios marcados como inactivos sin órdenes.</p>
          <button className="btn-danger" disabled={loading} onClick={() => run(cleanInactiveUsers)}>Eliminar</button>
        </div>

        <div className="update-card">
          <h4>Limpiar órdenes canceladas (masivo)</h4>
          <p className="card-note">Órdenes canceladas con más de 30 días.</p>
          <button className="btn-danger" disabled={loading} onClick={() => run(cleanCancelledOrders)}>Limpiar</button>
        </div>
      </div>

      <ResultBox result={result} />
    </div>
  );
}

// ── MAIN COMPONENT ───────────────────────────────────────────────
export default function Admin() {
  const [tab, setTab] = useState("create");

  const tabs = [
    { id: "create", label: "Crear" },
    { id: "read", label: "Consultar" },
    { id: "update", label: "Actualizar" },
    { id: "delete", label: "Eliminar" },
  ];

  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="page-title">Panel de Administración CRUD</h1>
        <p className="page-subtitle">Operaciones completas sobre las colecciones de la base de datos</p>
      </div>

      <div className="admin-tabs">
        {tabs.map((t) => (
          <button
            key={t.id}
            className={`admin-tab-btn ${tab === t.id ? "active" : ""}`}
            onClick={() => setTab(t.id)}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === "create" && <CreateTab />}
      {tab === "read" && <ReadTab />}
      {tab === "update" && <UpdateTab />}
      {tab === "delete" && <DeleteTab />}
    </div>
  );
}
