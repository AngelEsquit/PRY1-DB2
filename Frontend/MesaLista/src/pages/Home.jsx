import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import Hero from "../components/Hero";
import SearchBar from "../components/SearchBar";
import SectionTitle from "../components/SectionTitle";
import RestaurantCard from "../components/RestaurantCard";
import CategoryCard from "../components/CategoryCard";
import ReviewCard from "../components/ReviewCard";
import { fetchRestaurants, fetchReviews } from "../services/api";

function Home() {
  const navigate = useNavigate();
  const [search, setSearch] = useState("");
  const [restaurants, setRestaurants] = useState([]);
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadHomeData() {
      try {
        setLoading(true);
        const [restaurantData, reviewData] = await Promise.all([
          fetchRestaurants(),
          fetchReviews(),
        ]);
        setRestaurants(restaurantData);
        setReviews(reviewData);
      } catch {
        setRestaurants([]);
        setReviews([]);
      } finally {
        setLoading(false);
      }
    }

    loadHomeData();
  }, []);

  const filteredRestaurants = useMemo(() => {
    return restaurants.filter(
      (restaurant) =>
        (restaurant.nombre || "").toLowerCase().includes(search.toLowerCase()) ||
        (Array.isArray(restaurant.tipo_comida)
          ? restaurant.tipo_comida.join(" ").toLowerCase()
          : ""
        ).includes(search.toLowerCase())
    );
  }, [restaurants, search]);

  const categories = useMemo(() => {
    const counter = new Map();

    for (const restaurant of restaurants) {
      const tipos = Array.isArray(restaurant.tipo_comida) ? restaurant.tipo_comida : [];
      for (const tipo of tipos) {
        counter.set(tipo, (counter.get(tipo) || 0) + 1);
      }
    }

    return Array.from(counter.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 6)
      .map(([name, count], idx) => ({
        id: `${name}-${idx}`,
        name,
        rating: `${count} restaurante${count > 1 ? "s" : ""}`,
        image:
          "https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=1200&q=80",
      }));
  }, [restaurants]);

  return (
    <>
      <Navbar />
      <Hero />
      <SearchBar value={search} onChange={setSearch} />

      <SectionTitle title="Restaurantes Populares" />
      <section className="container grid-section">
        {loading && <p>Cargando restaurantes...</p>}
        {!loading &&
          filteredRestaurants.slice(0, 8).map((restaurant) => (
            <RestaurantCard
              key={restaurant._id}
              restaurant={{
                id: restaurant._id,
                name: restaurant.nombre,
                category: Array.isArray(restaurant.tipo_comida)
                  ? restaurant.tipo_comida.join(", ")
                  : "Sin categoría",
                rating: 4.5,
                image:
                  "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=1200&q=80",
              }}
            />
          ))}
      </section>

      <div className="container center-button">
        <button className="btn btn-primary" onClick={() => navigate("/restaurants")}>
          Ver Todos
        </button>
      </div>

      <SectionTitle title="Categorías" />
      <section className="container grid-section">
        {categories.map((category) => (
          <CategoryCard key={category.id} category={category} />
        ))}
      </section>

      <div className="container center-button">
        <button className="btn btn-primary" onClick={() => navigate("/restaurants")}>
          Ver Todas
        </button>
      </div>

      <SectionTitle title="Últimas Reseñas" />
      <section className="container review-grid">
        {loading && <p>Cargando reseñas...</p>}
        {!loading &&
          reviews.slice(0, 3).map((review) => (
            <ReviewCard
              key={review._id}
              review={{
                user: review.usuario_nombre || "Usuario",
                restaurant: review.restaurante_nombre || "Restaurante",
                comment: review.comentario,
                rating: review.calificacion_general,
              }}
            />
          ))}
      </section>

      <footer className="footer">
        <div className="container footer-content">
          <h2>MesaLista</h2>
          <p>Sistema de gestión de pedidos y reseñas de restaurantes.</p>
        </div>
      </footer>
    </>
  );
}

export default Home;