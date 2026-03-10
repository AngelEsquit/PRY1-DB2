import { useState } from "react";
import { fetchUsers, deleteUserWithCascade } from "../services/api";

export default function Transactions() {
  const [users, setUsers] = useState([]);
  const [loadingUsers, setLoadingUsers] = useState(false);
  const [selectedUser, setSelectedUser] = useState("");
  const [confirm, setConfirm] = useState(false);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const loadUsers = async () => {
    setLoadingUsers(true);
    try {
      setUsers(await fetchUsers());
    } catch {
      // ignore
    } finally {
      setLoadingUsers(false);
    }
  };

  const handleDelete = async () => {
    if (!selectedUser) return;
    setLoading(true);
    setResult(null);
    try {
      const data = await deleteUserWithCascade(selectedUser);
      setResult({ type: "ok", data });
      setConfirm(false);
      setSelectedUser("");
    } catch (e) {
      setResult({ type: "error", data: e.message });
    } finally {
      setLoading(false);
    }
  };

  const selectedUserObj = users.find((u) => u._id === selectedUser);

  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="page-title">Transacciones MongoDB</h1>
        <p className="page-subtitle">Operaciones atómicas multi-documento con sesiones de transacción</p>
      </div>

      {/* Transaction 1: Create order with points (link) */}
      <div className="transaction-card info-card">
        <h3>Transacción 1: Crear orden y actualizar puntos</h3>
        <p>
          Esta transacción ya está integrada en el flujo del carrito de compras. Cuando un usuario
          confirma una orden, se ejecuta atómicamente la inserción de la orden y la actualización
          de los puntos del usuario en una sola transacción MongoDB.
        </p>
        <div className="tx-badge tx-badge-active">Activa en el carrito de compras</div>
      </div>

      {/* Transaction 2: Cascade delete */}
      <div className="transaction-card">
        <h3>Transacción 2: Eliminar usuario con dependencias (cascada)</h3>
        <p>
          Elimina un usuario y, en la misma transacción atómica, elimina todas sus órdenes y reseñas.
          Si cualquier operación falla, toda la transacción se revierte.
        </p>

        <div className="tx-steps">
          <div className="tx-step">
            <span className="tx-step-number">1</span>
            <span>Eliminar todas las reseñas del usuario</span>
          </div>
          <div className="tx-step">
            <span className="tx-step-number">2</span>
            <span>Eliminar todas las órdenes del usuario</span>
          </div>
          <div className="tx-step">
            <span className="tx-step-number">3</span>
            <span>Eliminar el documento del usuario</span>
          </div>
        </div>

        <div className="tx-actions">
          <button className="btn-ghost" onClick={loadUsers} disabled={loadingUsers}>
            {loadingUsers ? "Cargando…" : "Cargar usuarios"}
          </button>

          {users.length > 0 && (
            <select
              value={selectedUser}
              onChange={(e) => { setSelectedUser(e.target.value); setConfirm(false); setResult(null); }}
            >
              <option value="">-- Seleccionar usuario --</option>
              {users.map((u) => (
                <option key={u._id} value={u._id}>
                  {u.nombre} {u.apellido} ({u.email})
                </option>
              ))}
            </select>
          )}

          {selectedUser && !confirm && (
            <button className="btn-danger" onClick={() => setConfirm(true)}>
              Eliminar con cascada
            </button>
          )}
        </div>

        {confirm && selectedUserObj && (
          <div className="confirm-box">
            <p>
              ¿Eliminar a <strong>{selectedUserObj.nombre} {selectedUserObj.apellido}</strong> junto
              con todas sus órdenes y reseñas? Esta acción no se puede deshacer.
            </p>
            <div className="confirm-buttons">
              <button className="btn-danger" disabled={loading} onClick={handleDelete}>
                {loading ? "Eliminando…" : "Confirmar eliminación"}
              </button>
              <button className="btn-ghost" onClick={() => setConfirm(false)}>Cancelar</button>
            </div>
          </div>
        )}

        {result && (
          <div className={`result-box ${result.type === "error" ? "result-error" : "result-ok"}`}>
            {result.type === "ok" ? (
              <div className="tx-result">
                <p>Transacción completada exitosamente</p>
                <ul>
                  <li>Usuario eliminado: <strong>{result.data.usuario_eliminado ? "Sí" : "No"}</strong></li>
                  <li>Órdenes eliminadas: <strong>{result.data.ordenes_eliminadas ?? 0}</strong></li>
                  <li>Reseñas eliminadas: <strong>{result.data.resenas_eliminadas ?? 0}</strong></li>
                </ul>
              </div>
            ) : (
              <pre>{result.data}</pre>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
