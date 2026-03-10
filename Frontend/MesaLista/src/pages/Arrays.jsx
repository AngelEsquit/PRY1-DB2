import { useState } from "react";
import {
  fetchUsers,
  fetchRestaurants,
  fetchReviews,
  addUserPreference,
  removeUserPreference,
  addRestaurantSchedule,
  addReviewReply,
  removeReviewReply,
} from "../services/api";

function ResultBox({ result }) {
  if (!result) return null;
  return (
    <div className={`result-box ${result.type === "error" ? "result-error" : "result-ok"}`}>
      <pre>{typeof result.data === "string" ? result.data : JSON.stringify(result.data, null, 2)}</pre>
    </div>
  );
}

function ArraySection({ title, description, children }) {
  return (
    <div className="array-card">
      <h3>{title}</h3>
      <p className="card-note">{description}</p>
      {children}
    </div>
  );
}

export default function Arrays() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  // Form states
  const [addPref, setAddPref] = useState({ usuario_id: "", preferencia: "" });
  const [remPref, setRemPref] = useState({ usuario_id: "", preferencia: "" });
  const [sched, setSched] = useState({ restaurante_id: "", dia: "Lunes", apertura: "08:00", cierre: "22:00" });
  const [addReply, setAddReply] = useState({ resena_id: "", texto: "", autor: "Restaurante" });
  const [remReply, setRemReply] = useState({ resena_id: "", texto: "" });

  // Quick-load selectors
  const [users, setUsers] = useState([]);
  const [restaurants, setRestaurants] = useState([]);
  const [reviews, setReviews] = useState([]);
  const [loadingData, setLoadingData] = useState(false);

  const loadUsers = async () => { setLoadingData(true); try { setUsers(await fetchUsers()); } finally { setLoadingData(false); } };
  const loadRestaurants = async () => { setLoadingData(true); try { setRestaurants(await fetchRestaurants()); } finally { setLoadingData(false); } };
  const loadReviews = async () => { setLoadingData(true); try { setReviews(await fetchReviews()); } finally { setLoadingData(false); } };

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

  const DAYS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"];

  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="page-title">Operaciones con Arrays</h1>
        <p className="page-subtitle">Manipulación de arreglos embebidos en documentos MongoDB ($push, $pull)</p>
      </div>

      <div className="arrays-grid">
        {/* Add preference */}
        <ArraySection title="Agregar preferencia a usuario" description="Añade un string al array 'preferencias' del usuario ($push)">
          <div className="quick-load">
            <button className="btn-ghost" onClick={loadUsers} disabled={loadingData}>Cargar usuarios</button>
            {users.length > 0 && (
              <select onChange={e => setAddPref(p => ({ ...p, usuario_id: e.target.value }))}>
                <option value="">-- Seleccionar --</option>
                {users.map(u => <option key={u._id} value={u._id}>{u.nombre} {u.apellido}</option>)}
              </select>
            )}
          </div>
          <input placeholder="ID usuario" value={addPref.usuario_id} onChange={e => setAddPref(p => ({ ...p, usuario_id: e.target.value }))} />
          <input placeholder="Nueva preferencia (ej: Vegano)" value={addPref.preferencia} onChange={e => setAddPref(p => ({ ...p, preferencia: e.target.value }))} />
          <button className="btn-primary" disabled={loading} onClick={() => run(() => addUserPreference(addPref.usuario_id, addPref.preferencia))}>Agregar</button>
        </ArraySection>

        {/* Remove preference */}
        <ArraySection title="Eliminar preferencia de usuario" description="Elimina un string del array 'preferencias' ($pull)">
          <div className="quick-load">
            <button className="btn-ghost" onClick={loadUsers} disabled={loadingData}>Cargar usuarios</button>
            {users.length > 0 && (
              <select onChange={e => setRemPref(p => ({ ...p, usuario_id: e.target.value }))}>
                <option value="">-- Seleccionar --</option>
                {users.map(u => <option key={u._id} value={u._id}>{u.nombre} {u.apellido}</option>)}
              </select>
            )}
          </div>
          <input placeholder="ID usuario" value={remPref.usuario_id} onChange={e => setRemPref(p => ({ ...p, usuario_id: e.target.value }))} />
          <input placeholder="Preferencia a eliminar" value={remPref.preferencia} onChange={e => setRemPref(p => ({ ...p, preferencia: e.target.value }))} />
          <button className="btn-danger" disabled={loading} onClick={() => run(() => removeUserPreference(remPref.usuario_id, remPref.preferencia))}>Eliminar</button>
        </ArraySection>

        {/* Add schedule */}
        <ArraySection title="Agregar horario a restaurante" description="Añade un objeto al array 'horario' del restaurante ($push)">
          <div className="quick-load">
            <button className="btn-ghost" onClick={loadRestaurants} disabled={loadingData}>Cargar restaurantes</button>
            {restaurants.length > 0 && (
              <select onChange={e => setSched(p => ({ ...p, restaurante_id: e.target.value }))}>
                <option value="">-- Seleccionar --</option>
                {restaurants.map(r => <option key={r._id} value={r._id}>{r.nombre}</option>)}
              </select>
            )}
          </div>
          <input placeholder="ID restaurante" value={sched.restaurante_id} onChange={e => setSched(p => ({ ...p, restaurante_id: e.target.value }))} />
          <label>Día
            <select value={sched.dia} onChange={e => setSched(p => ({ ...p, dia: e.target.value }))}>
              {DAYS.map(d => <option key={d} value={d}>{d}</option>)}
            </select>
          </label>
          <label>Apertura <input type="time" value={sched.apertura} onChange={e => setSched(p => ({ ...p, apertura: e.target.value }))} /></label>
          <label>Cierre <input type="time" value={sched.cierre} onChange={e => setSched(p => ({ ...p, cierre: e.target.value }))} /></label>
          <button className="btn-primary" disabled={loading} onClick={() => run(() => addRestaurantSchedule(sched.restaurante_id, sched.dia, sched.apertura, sched.cierre))}>Agregar horario</button>
        </ArraySection>

        {/* Add reply */}
        <ArraySection title="Agregar respuesta a reseña" description="Añade un objeto al array 'respuestas' de la reseña ($push)">
          <div className="quick-load">
            <button className="btn-ghost" onClick={loadReviews} disabled={loadingData}>Cargar reseñas</button>
            {reviews.length > 0 && (
              <select onChange={e => setAddReply(p => ({ ...p, resena_id: e.target.value }))}>
                <option value="">-- Seleccionar --</option>
                {reviews.map(r => <option key={r._id} value={r._id}>{r.titulo} – {r.restaurante_nombre}</option>)}
              </select>
            )}
          </div>
          <input placeholder="ID reseña" value={addReply.resena_id} onChange={e => setAddReply(p => ({ ...p, resena_id: e.target.value }))} />
          <textarea placeholder="Texto de la respuesta" value={addReply.texto} onChange={e => setAddReply(p => ({ ...p, texto: e.target.value }))} rows={3} />
          <input placeholder="Autor (ej: Restaurante)" value={addReply.autor} onChange={e => setAddReply(p => ({ ...p, autor: e.target.value }))} />
          <button className="btn-primary" disabled={loading} onClick={() => run(() => addReviewReply(addReply.resena_id, addReply.texto, addReply.autor))}>Agregar respuesta</button>
        </ArraySection>

        {/* Remove reply */}
        <ArraySection title="Eliminar respuesta de reseña" description="Elimina por texto exacto del array 'respuestas' ($pull)">
          <div className="quick-load">
            <button className="btn-ghost" onClick={loadReviews} disabled={loadingData}>Cargar reseñas</button>
            {reviews.length > 0 && (
              <select onChange={e => setRemReply(p => ({ ...p, resena_id: e.target.value }))}>
                <option value="">-- Seleccionar --</option>
                {reviews.map(r => <option key={r._id} value={r._id}>{r.titulo} – {r.restaurante_nombre}</option>)}
              </select>
            )}
          </div>
          <input placeholder="ID reseña" value={remReply.resena_id} onChange={e => setRemReply(p => ({ ...p, resena_id: e.target.value }))} />
          <textarea placeholder="Texto exacto de la respuesta a eliminar" value={remReply.texto} onChange={e => setRemReply(p => ({ ...p, texto: e.target.value }))} rows={3} />
          <button className="btn-danger" disabled={loading} onClick={() => run(() => removeReviewReply(remReply.resena_id, remReply.texto))}>Eliminar respuesta</button>
        </ArraySection>
      </div>

      <ResultBox result={result} />
    </div>
  );
}
