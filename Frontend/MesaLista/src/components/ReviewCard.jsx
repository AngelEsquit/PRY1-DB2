import StarRating from "./StarRating";

function ReviewCard({ review }) {
  return (
    <article className="review-card">
      <h3>{review.user}</h3>
      <p className="review-restaurant">{review.restaurant}</p>
      <StarRating rating={review.rating} />
      <p>{review.comment}</p>
    </article>
  );
}

export default ReviewCard;