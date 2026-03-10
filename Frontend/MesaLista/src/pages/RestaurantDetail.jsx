import { useCallback, useEffect, useMemo, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import MenuItemCard from "../components/MenuItemCard";
import ReviewCard from "../components/ReviewCard";
import ReviewForm from "../components/ReviewForm";
import QuantityModal from "../components/QuantityModal";
import StarRating from "../components/StarRating";
import { fetchRestaurantDetail, fetchReviews } from "../services/api";

function RestaurantDetail() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [restaurant, setRestaurant] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [loadingRestaurant, setLoadingRestaurant] = useState(true);
  const [loadingReviews, setLoadingReviews] = useState(true);
  const [error, setError] = useState("");

  const [selectedItem, setSelectedItem] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  useEffect(() => {
    async function loadRestaurant() {
      try {
        setLoadingRestaurant(true);
        const data = await fetchRestaurantDetail(id);
        setRestaurant(data);
        setError("");
      } catch (err) {
        setError(err.message || "No se pudo cargar el restaurante");
      } finally {
        setLoadingRestaurant(false);
      }
    }

    loadRestaurant();
  }, [id]);

  const loadReviews = useCallback(async () => {
    try {
      setLoadingReviews(true);
      const data = await fetchReviews();
      setReviews(data);
    } catch {
      setReviews([]);
    } finally {
      setLoadingReviews(false);
    }
  }, []);

  useEffect(() => {
    loadReviews();
  }, [loadReviews]);

  const restaurantReviews = useMemo(() => {
    return reviews.filter((review) => review.restaurante_id === id);
  }, [reviews, id]);

  const handleOpenModal = (item) => {
    setSelectedItem(item);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setSelectedItem(null);
    setIsModalOpen(false);
  };

  if (loadingRestaurant) {
    return (
      <>
        <Navbar />
        <section className="container page-header">
          <h2>Cargando restaurante...</h2>
        </section>
      </>
    );
  }

  if (error || !restaurant) {
    return (
      <>
        <Navbar />
        <section className="container page-header">
          <h2>Restaurante no encontrado</h2>
          {error && <p className="error-text">{error}</p>}
        </section>
      </>
    );
  }

  const menu = Array.isArray(restaurant.menu) ? restaurant.menu : [];

  return (
    <>
      <Navbar />

      <section className="container restaurant-detail">
        <div className="restaurant-top">
          <img
            src="https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=1200&q=80"
            alt={restaurant.nombre}
            className="restaurant-detail-image"
          />

          <div className="restaurant-detail-info">
            <h2>{restaurant.nombre}</h2>
            <StarRating rating={4.5} />
            <p>
              <strong>Tipo de comida:</strong>{" "}
              {Array.isArray(restaurant.tipo_comida)
                ? restaurant.tipo_comida.join(", ")
                : "No disponible"}
            </p>
            <p>
              <strong>Ubicación:</strong>{" "}
              {restaurant.direccion?.ciudad || "No disponible"}
            </p>
            <p>
              <strong>Correo:</strong> {restaurant.email || "No disponible"}
            </p>
            <p>
              <strong>Teléfono:</strong> {restaurant.telefono || "No disponible"}
            </p>
            <p>{restaurant.descripcion || "Sin descripción"}</p>

            <button className="btn btn-primary" onClick={() => navigate("/cart")}>
              Ir al carrito
            </button>
          </div>
        </div>

        <div className="restaurant-section">
          <h3>Menú</h3>

          {menu.length === 0 ? (
            <p>Este restaurante no tiene artículos disponibles.</p>
          ) : (
            <div className="menu-grid">
              {menu.map((item) => (
                <MenuItemCard
                  key={item._id}
                  item={{
                    id: item._id,
                    name: item.nombre,
                    description: item.descripcion,
                    price: Number(item.precio),
                    image:
                      "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=1200&q=80",
                  }}
                  onOpenModal={handleOpenModal}
                />
              ))}
            </div>
          )}
        </div>

        <div className="restaurant-section">
          <ReviewForm
            restaurant={{
              id: restaurant._id,
              name: restaurant.nombre,
            }}
            onReviewCreated={loadReviews}
          />
        </div>

        <div className="restaurant-section">
          <h3>Reseñas</h3>

          {loadingReviews && <p>Cargando reseñas...</p>}

          {!loadingReviews && restaurantReviews.length === 0 && (
            <p>Este restaurante aún no tiene reseñas.</p>
          )}

          {!loadingReviews && restaurantReviews.length > 0 && (
            <div className="review-grid">
              {restaurantReviews.map((review) => (
                <ReviewCard
                  key={review._id}
                  review={{
                    user: review.usuario_nombre || "Usuario",
                    restaurant: review.restaurante_nombre || restaurant.nombre,
                    comment: review.comentario,
                    rating: review.calificacion_general,
                  }}
                />
              ))}
            </div>
          )}
        </div>
      </section>

      <QuantityModal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        restaurant={{
          id: restaurant._id,
          name: restaurant.nombre,
        }}
        item={selectedItem}
      />
    </>
  );
}

export default RestaurantDetail;