import { useNavigate } from "react-router-dom";

function Hero() {
  const navigate = useNavigate();

  return (
    <section className="hero">
      <div className="container hero-content">
        <div className="hero-text">
          <h2>Descubre restaurantes, crea órdenes y analiza reseñas en un solo lugar</h2>
          <h3>MesaLista</h3>

          <div className="hero-buttons">
            <button
              className="btn btn-accent"
              onClick={() => navigate("/restaurants")}
            >
              Ver Restaurantes
            </button>

            <button
              className="btn btn-light"
              onClick={() => navigate("/cart")}
            >
              Ir al carrito
            </button>
          </div>
        </div>

        <div className="hero-image">
          <img
            src="https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=1200&q=80"
            alt="Plato de comida"
          />
        </div>
      </div>
    </section>
  );
}

export default Hero;