import { useMemo, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import MenuItemCard from "../components/MenuItemCard";
import ReviewCard from "../components/ReviewCard";
import ReviewForm from "../components/ReviewForm";
import QuantityModal from "../components/QuantityModal";
import StarRating from "../components/StarRating";
import { restaurants } from "../data/mockData";
import { useReviews } from "../context/ReviewContext";

function RestaurantDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { reviews } = useReviews();

  const [selectedItem, setSelectedItem] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const restaurant = restaurants.find((r) => r.id === Number(id));

  const restaurantReviews = useMemo(() => {
    return reviews.filter((review) => review.restaurantId === Number(id));
  }, [reviews, id]);

  const handleOpenModal = (item) => {
    setSelectedItem(item);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setSelectedItem(null);
    setIsModalOpen(false);
  };

  if (!restaurant) {
    return (
      <>
        <Navbar />
        <section className="container page-header">
          <h2>Restaurante no encontrado</h2>
        </section>
      </>
    );
  }

  return (
    <>
      <Navbar />

      <section className="container restaurant-detail">
        <div className="restaurant-top">
          <img
            src={restaurant.image}
            alt={restaurant.name}
            className="restaurant-detail-image"
          />

          <div className="restaurant-detail-info">
            <h2>{restaurant.name}</h2>
            <StarRating rating={restaurant.rating} />
            <p><strong>Categoría:</strong> {restaurant.category}</p>
            <p><strong>Ubicación:</strong> {restaurant.location}</p>
            <p><strong>Horario:</strong> {restaurant.hours}</p>
            <p>{restaurant.description}</p>

            <button className="btn btn-primary" onClick={() => navigate("/cart")}>
              Ir al carrito
            </button>
          </div>
        </div>

        <div className="restaurant-section">
          <h3>Menú</h3>
          <div className="menu-grid">
            {restaurant.menu.map((item) => (
              <MenuItemCard
                key={item.id}
                item={item}
                onOpenModal={handleOpenModal}
              />
            ))}
          </div>
        </div>

        <div className="restaurant-section">
          <ReviewForm restaurant={restaurant} />
        </div>

        <div className="restaurant-section">
          <h3>Reseñas</h3>
          <div className="review-grid">
            {restaurantReviews.map((review) => (
              <ReviewCard key={review.id} review={review} />
            ))}
          </div>
        </div>
      </section>

      <QuantityModal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        restaurant={restaurant}
        item={selectedItem}
      />
    </>
  );
}

export default RestaurantDetail;