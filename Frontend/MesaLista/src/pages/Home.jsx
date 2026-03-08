import { useMemo, useState } from "react";
import Navbar from "../components/Navbar";
import Hero from "../components/Hero";
import SearchBar from "../components/SearchBar";
import SectionTitle from "../components/SectionTitle";
import RestaurantCard from "../components/RestaurantCard";
import CategoryCard from "../components/CategoryCard";
import ReviewCard from "../components/ReviewCard";
import { restaurants, categories } from "../data/mockData";
import { useReviews } from "../context/ReviewContext";

function Home() {
  const [search, setSearch] = useState("");
  const { reviews } = useReviews();

  const filteredRestaurants = useMemo(() => {
    return restaurants.filter(
      (restaurant) =>
        restaurant.name.toLowerCase().includes(search.toLowerCase()) ||
        restaurant.category.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <>
      <Navbar />
      <Hero />
      <SearchBar value={search} onChange={setSearch} />

      <SectionTitle title="Restaurantes Populares" />
      <section className="container grid-section">
        {filteredRestaurants.map((restaurant) => (
          <RestaurantCard key={restaurant.id} restaurant={restaurant} />
        ))}
      </section>

      <div className="container center-button">
        <button className="btn btn-primary">Ver Todos</button>
      </div>

      <SectionTitle title="Categorías" />
      <section className="container grid-section">
        {categories.map((category) => (
          <CategoryCard key={category.id} category={category} />
        ))}
      </section>

      <div className="container center-button">
        <button className="btn btn-primary">Ver Todas</button>
      </div>

      <SectionTitle title="Últimas Reseñas" />
      <section className="container review-grid">
        {reviews.slice(0, 3).map((review) => (
          <ReviewCard key={review.id} review={review} />
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