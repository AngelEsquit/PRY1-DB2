import { useEffect, useState } from "react";
import Navbar from "../components/Navbar";
import ReviewCard from "../components/ReviewCard";
import { fetchReviews } from "../services/api";

function Reviews() {
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadReviews() {
      try {
        setLoading(true);
        const data = await fetchReviews();
        setReviews(data);
        setError("");
      } catch (err) {
        setError(err.message || "No se pudieron cargar las reseñas");
      } finally {
        setLoading(false);
      }
    }

    loadReviews();
  }, []);

  return (
    <>
      <Navbar />

      <section className="page-header container">
        <h2>Reseñas</h2>
        <p>Lee las opiniones recientes de otros usuarios.</p>
      </section>

      <section className="container review-grid page-section">
        {loading && <p>Cargando reseñas...</p>}
        {error && <p className="error-text">{error}</p>}

        {!loading &&
          !error &&
          reviews.map((review) => (
            <ReviewCard
              key={review._id}
              review={{
                user: review.usuario_nombre || "Usuario",
                restaurant: review.restaurante_nombre || review.restaurante_id,
                comment: review.comentario,
                rating: review.calificacion_general,
              }}
            />
          ))}
      </section>
    </>
  );
}

export default Reviews;