import { useState } from "react";
import { fetchIndexComparison } from "../services/api";

function ImprovementBadge({ pct }) {
  if (pct === null || pct === undefined) return <span className="badge badge-neutral">N/A</span>;
  if (pct > 0) return <span className="badge badge-green">+{pct}%</span>;
  if (pct < 0) return <span className="badge badge-red">{pct}%</span>;
  return <span className="badge badge-neutral">0%</span>;
}

function MetricsCell({ metrics }) {
  if (!metrics) return <td>—</td>;
  return (
    <td>
      <div className="metrics-cell">
        <div><span className="metric-label">Tiempo:</span> <strong>{metrics.time_ms ?? "?"} ms</strong></div>
        <div><span className="metric-label">Docs examinados:</span> {metrics.docs_examined ?? "?"}</div>
        <div><span className="metric-label">Keys examinadas:</span> {metrics.keys_examined ?? "?"}</div>
        {metrics.index_used && <div><span className="metric-label">Índice:</span> <code>{metrics.index_used}</code></div>}
      </div>
    </td>
  );
}

export default function Indices() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const runComparison = async () => {
    setLoading(true);
    setError(null);
    setData(null);
    try {
      setData(await fetchIndexComparison());
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="page-title">Comparación de Índices</h1>
        <p className="page-subtitle">
          Demo de rendimiento: consultas con y sin índice usando <code>explain()</code> de MongoDB
        </p>
      </div>

      <div className="indices-controls">
        <button className="btn-primary btn-large" onClick={runComparison} disabled={loading}>
          {loading ? "Ejecutando comparación…" : "Ejecutar comparación de índices"}
        </button>
        {data && (
          <p className="tip-text">{data.tip}</p>
        )}
      </div>

      {error && (
        <div className="result-box result-error">
          <p>{error}</p>
        </div>
      )}

      {loading && (
        <div className="loading-overlay">
          <div className="loading-spinner" />
          <p>Ejecutando 10 comparaciones en la base de datos…</p>
        </div>
      )}

      {data && data.results && (
        <div className="indices-results">
          <div className="table-scroll">
            <table className="indices-table">
              <thead>
                <tr>
                  <th>Caso</th>
                  <th>Sin índice</th>
                  <th>Con índice</th>
                  <th>Mejora</th>
                  <th>Índice detectado</th>
                </tr>
              </thead>
              <tbody>
                {data.results.map((row, i) => (
                  <tr key={i} className={row.mejora_pct > 0 ? "row-improved" : ""}>
                    <td className="index-label">{row.label}</td>
                    <MetricsCell metrics={row.sin_indice} />
                    <MetricsCell metrics={row.con_indice} />
                    <td className="improvement-cell">
                      <ImprovementBadge pct={row.mejora_pct} />
                    </td>
                    <td><code className="index-name">{row.indice_detectado || "—"}</code></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="indices-legend">
            <h4>Leyenda de tipos de índice</h4>
            <ul>
              <li><strong>Índice simple:</strong> Campo único, búsqueda O(log n).</li>
              <li><strong>Índice compuesto:</strong> Múltiples campos, ideal para filtros combinados.</li>
              <li><strong>Índice geoespacial (2dsphere):</strong> Consultas por proximidad geográfica.</li>
              <li><strong>Índice de texto:</strong> Búsqueda full-text sobre strings de texto libre.</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}
