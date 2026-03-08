import { useNavigate } from "react-router-dom";
import StarRating from "./StarRating";

function RestaurantCard({ restaurant }) {
  const navigate = useNavigate();

  return (
    <article className="card">
      <img src={restaurant.image} alt={restaurant.name} className="card-image" />

      <div className="card-body">
        <h3>{restaurant.name}</h3>
        <StarRating rating={restaurant.rating} />
        <p>{restaurant.category}</p>

        <button
          className="btn btn-accent full-width"
          onClick={() => navigate(`/restaurants/${restaurant.id}`)}
        >
          Ver Detalle
        </button>
      </div>
    </article>
  );
}

export default RestaurantCard;