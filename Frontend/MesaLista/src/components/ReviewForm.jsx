import { useEffect, useState } from "react";
import { createReview, fetchUsers } from "../services/api";

function ReviewForm({ restaurant, onReviewCreated }) {
  const [usuarioId, setUsuarioId] = useState("");
  const [titulo, setTitulo] = useState("");
  const [comment, setComment] = useState("");
  const [rating, setRating] = useState(5);
  const [loading, setLoading] = useState(false);
  const [users, setUsers] = useState([]);

  useEffect(() => {
    async function loadUsers() {
      try {
        const data = await fetchUsers();
        setUsers(data);
      } catch {
        setUsers([]);
      }
    }

    loadUsers();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!usuarioId.trim() || !titulo.trim() || !comment.trim()) {
      alert("Completa todos los campos");
      return;
    }

    try {
      setLoading(true);

      await createReview({
        usuario_id: usuarioId,
        restaurante_id: restaurant.id,
        calificacion: Number(rating),
        titulo,
        comentario: comment,
      });

      setUsuarioId("");
      setTitulo("");
      setComment("");
      setRating(5);

      if (onReviewCreated) {
        onReviewCreated();
      }

      alert("Reseña agregada con éxito");
    } catch (err) {
      alert(err.message || "No se pudo crear la reseña");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form className="review-form" onSubmit={handleSubmit}>
      <h3>Crear reseña</h3>

      <select
        value={usuarioId}
        onChange={(e) => setUsuarioId(e.target.value)}
        className="form-input"
      >
        <option value="">Selecciona un usuario</option>
        {users.map((user) => (
          <option key={user._id} value={user._id}>
            {user.nombre} {user.apellido} ({user.email})
          </option>
        ))}
      </select>

      <input
        type="text"
        placeholder="Título de la reseña"
        value={titulo}
        onChange={(e) => setTitulo(e.target.value)}
        className="form-input"
      />

      <select
        value={rating}
        onChange={(e) => setRating(e.target.value)}
        className="form-input"
      >
        <option value={5}>5 estrellas</option>
        <option value={4}>4 estrellas</option>
        <option value={3}>3 estrellas</option>
        <option value={2}>2 estrellas</option>
        <option value={1}>1 estrella</option>
      </select>

      <textarea
        placeholder="Escribe tu comentario"
        value={comment}
        onChange={(e) => setComment(e.target.value)}
        className="form-input form-textarea"
      />

      <button type="submit" className="btn btn-primary" disabled={loading}>
        {loading ? "Publicando..." : "Publicar reseña"}
      </button>
    </form>
  );
}

export default ReviewForm;