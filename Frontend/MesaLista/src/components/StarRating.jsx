function StarRating({ rating }) {
  const fullStars = Math.floor(rating);
  const hasHalf = rating % 1 >= 0.5;
  const emptyStars = 5 - fullStars - (hasHalf ? 1 : 0);

  return (
    <div className="star-rating">
      {"★".repeat(fullStars)}
      {hasHalf ? "☆" : ""}
      {"✩".repeat(emptyStars)}
      <span className="star-number">{rating.toFixed(1)}</span>
    </div>
  );
}

export default StarRating;