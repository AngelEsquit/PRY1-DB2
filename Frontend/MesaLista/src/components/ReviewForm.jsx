import { useState } from "react";
import { useReviews } from "../context/ReviewContext";

function ReviewForm({ restaurant }) {
  const { addReview } = useReviews();
  const [user, setUser] = useState("");
  const [comment, setComment] = useState("");
  const [rating, setRating] = useState(5);

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!user.trim() || !comment.trim()) {
      alert("Completa todos los campos");
      return;
    }

    addReview({
      user,
      restaurant: restaurant.name,
      restaurantId: restaurant.id,
      comment,
      rating: Number(rating),
    });

    setUser("");
    setComment("");
    setRating(5);
    alert("Reseña agregada");
  };

  return (
    <form className="review-form" onSubmit={handleSubmit}>
      <h3>Crear reseña</h3>

      <input
        type="text"
        placeholder="Tu nombre"
        value={user}
        onChange={(e) => setUser(e.target.value)}
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

      <button type="submit" className="btn btn-primary">
        Publicar reseña
      </button>
    </form>
  );
}

export default ReviewForm;