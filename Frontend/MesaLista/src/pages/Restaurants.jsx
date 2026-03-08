import { useMemo, useState } from "react";
import Navbar from "../components/Navbar";
import SearchBar from "../components/SearchBar";
import RestaurantCard from "../components/RestaurantCard";
import { restaurants } from "../data/mockData";

function Restaurants() {
  const [search, setSearch] = useState("");

  const filteredRestaurants = useMemo(() => {
    return restaurants.filter(
      (restaurant) =>
        restaurant.name.toLowerCase().includes(search.toLowerCase()) ||
        restaurant.category.toLowerCase().includes(search.toLowerCase()) ||
        restaurant.location.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <>
      <Navbar />

      <section className="page-header container">
        <h2>Restaurantes</h2>
        <p>Explora los restaurantes disponibles en MesaLista.</p>
      </section>

      <SearchBar
        value={search}
        onChange={setSearch}
        placeholder="Buscar por nombre, categoría o ubicación..."
      />

      <section className="container grid-section page-section">
        {filteredRestaurants.map((restaurant) => (
          <RestaurantCard key={restaurant.id} restaurant={restaurant} />
        ))}
      </section>
    </>
  );
}

export default Restaurants;