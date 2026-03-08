import Navbar from "../components/Navbar";
import ReviewCard from "../components/ReviewCard";
import { useReviews } from "../context/ReviewContext";

function Reviews() {
  const { reviews } = useReviews();

  return (
    <>
      <Navbar />

      <section className="page-header container">
        <h2>Reseñas</h2>
        <p>Lee las opiniones recientes de otros usuarios.</p>
      </section>

      <section className="container review-grid page-section">
        {reviews.map((review) => (
          <ReviewCard key={review.id} review={review} />
        ))}
      </section>
    </>
  );
}

export default Reviews;