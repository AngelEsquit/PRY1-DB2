import { useState, useEffect, useCallback } from "react";
import {
  listGridFSFiles,
  uploadGridFSFile,
  getGridFSFileInfo,
  getGridFSDownloadURL,
  deleteGridFSFile,
} from "../services/api";

function formatBytes(bytes) {
  if (bytes === 0) return "0 B";
  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
}

function formatDate(iso) {
  if (!iso) return "—";
  return new Date(iso).toLocaleString("es-GT");
}

export default function GridFS() {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadMsg, setUploadMsg] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileInfo, setFileInfo] = useState(null);
  const [infoLoading, setInfoLoading] = useState(false);

  const loadFiles = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setFiles(await listGridFSFiles());
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { loadFiles(); }, [loadFiles]);

  const handleUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setUploadMsg(null);
    try {
      const res = await uploadGridFSFile(file);
      setUploadMsg({ type: "ok", text: `Archivo subido: ${res.filename} (ID: ${res.file_id})` });
      loadFiles();
    } catch (ex) {
      setUploadMsg({ type: "error", text: ex.message });
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  };

  const handleDelete = async (fileId) => {
    if (!window.confirm("¿Eliminar este archivo de GridFS?")) return;
    try {
      await deleteGridFSFile(fileId);
      setFiles((prev) => prev.filter((f) => f.file_id !== fileId));
      if (fileInfo?.file_id === fileId) setFileInfo(null);
    } catch (ex) {
      alert(ex.message);
    }
  };

  const handleInfo = async (fileId) => {
    if (fileInfo?.file_id === fileId) { setFileInfo(null); return; }
    setInfoLoading(true);
    try {
      setFileInfo(await getGridFSFileInfo(fileId));
      setSelectedFile(fileId);
    } catch (ex) {
      alert(ex.message);
    } finally {
      setInfoLoading(false);
    }
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="page-title">Gestor de Archivos GridFS</h1>
        <p className="page-subtitle">Almacenamiento de archivos binarios en MongoDB mediante GridFS</p>
      </div>

      {/* Upload */}
      <div className="gridfs-upload-zone">
        <h3>Subir archivo</h3>
        <p className="card-note">Los archivos se almacenan distribuidos en chunks dentro de MongoDB (colecciones fs.files y fs.chunks).</p>
        <label className="upload-btn">
          {uploading ? "Subiendo…" : "Seleccionar archivo"}
          <input type="file" hidden onChange={handleUpload} disabled={uploading} />
        </label>
        {uploadMsg && (
          <div className={`upload-msg ${uploadMsg.type === "error" ? "result-error" : "result-ok"}`}>
            {uploadMsg.text}
          </div>
        )}
      </div>

      {/* File list */}
      <div className="gridfs-list">
        <div className="gridfs-list-header">
          <h3>Archivos almacenados ({files.length})</h3>
          <button className="btn-ghost" onClick={loadFiles} disabled={loading}>
            {loading ? "Actualizando…" : "Actualizar lista"}
          </button>
        </div>

        {error && <div className="result-box result-error"><pre>{error}</pre></div>}

        {files.length === 0 && !loading && (
          <div className="empty-state">No hay archivos en GridFS. Sube el primero.</div>
        )}

        {files.length > 0 && (
          <div className="table-scroll">
            <table className="admin-table">
              <thead>
                <tr>
                  <th>Nombre</th>
                  <th>Tamaño</th>
                  <th>Fecha de subida</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {files.map((f) => (
                  <tr key={f.file_id} className={selectedFile === f.file_id ? "row-selected" : ""}>
                    <td className="file-name">{f.filename}</td>
                    <td>{formatBytes(f.length)}</td>
                    <td>{formatDate(f.upload_date)}</td>
                    <td className="file-actions">
                      <a
                        href={getGridFSDownloadURL(f.file_id)}
                        className="btn-icon btn-download"
                        download={f.filename}
                        title="Descargar"
                      >
                        ↓
                      </a>
                      <button
                        className={`btn-icon ${selectedFile === f.file_id ? "btn-info-active" : "btn-info"}`}
                        onClick={() => handleInfo(f.file_id)}
                        disabled={infoLoading}
                        title="Ver información"
                      >
                        ℹ
                      </button>
                      <button
                        className="btn-icon btn-del"
                        onClick={() => handleDelete(f.file_id)}
                        title="Eliminar"
                      >
                        ✕
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* File info panel */}
        {fileInfo && (
          <div className="file-info-panel">
            <h4>Información del archivo</h4>
            <dl className="info-dl">
              <dt>ID</dt><dd>{fileInfo.file_id}</dd>
              <dt>Nombre</dt><dd>{fileInfo.filename}</dd>
              <dt>Tamaño</dt><dd>{formatBytes(fileInfo.length)}</dd>
              <dt>Fecha de subida</dt><dd>{formatDate(fileInfo.upload_date)}</dd>
              {fileInfo.metadata && Object.keys(fileInfo.metadata).length > 0 && (
                <>
                  <dt>Metadatos</dt>
                  <dd><pre>{JSON.stringify(fileInfo.metadata, null, 2)}</pre></dd>
                </>
              )}
            </dl>
          </div>
        )}
      </div>
    </div>
  );
}
