import { useEffect, useMemo, useState } from "react";
import Navbar from "../components/Navbar";
import SearchBar from "../components/SearchBar";
import RestaurantCard from "../components/RestaurantCard";
import { fetchRestaurants } from "../services/api";

function Restaurants() {
  const [search, setSearch] = useState("");
  const [restaurants, setRestaurants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadRestaurants() {
      try {
        setLoading(true);
        const data = await fetchRestaurants();
        setRestaurants(data);
        setError("");
      } catch (err) {
        setError(err.message || "No se pudieron cargar los restaurantes");
      } finally {
        setLoading(false);
      }
    }

    loadRestaurants();
  }, []);

  const filteredRestaurants = useMemo(() => {
    return restaurants.filter((restaurant) => {
      const nombre = restaurant.nombre?.toLowerCase() || "";
      const descripcion = restaurant.descripcion?.toLowerCase() || "";
      const ciudad = restaurant.direccion?.ciudad?.toLowerCase() || "";
      const tipoComida = Array.isArray(restaurant.tipo_comida)
        ? restaurant.tipo_comida.join(" ").toLowerCase()
        : "";

      const query = search.toLowerCase();

      return (
        nombre.includes(query) ||
        descripcion.includes(query) ||
        ciudad.includes(query) ||
        tipoComida.includes(query)
      );
    });
  }, [restaurants, search]);

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
        placeholder="Buscar por nombre, tipo de comida o ciudad..."
      />

      <section className="container page-section">
        {loading && <p>Cargando restaurantes...</p>}
        {error && <p className="error-text">{error}</p>}

        {!loading && !error && filteredRestaurants.length === 0 && (
          <p>No se encontraron restaurantes.</p>
        )}

        {!loading && !error && filteredRestaurants.length > 0 && (
          <div className="grid-section">
            {filteredRestaurants.map((restaurant) => (
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
          </div>
        )}
      </section>
    </>
  );
}

export default Restaurants;