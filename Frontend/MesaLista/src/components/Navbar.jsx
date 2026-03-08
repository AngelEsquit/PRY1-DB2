import { NavLink, useNavigate } from "react-router-dom";
import { useCart } from "../context/CartContext";

function Navbar() {
  const navigate = useNavigate();
  const { itemCount } = useCart();

  return (
    <header className="navbar">
      <div className="container navbar-content">
        <h1 className="logo" onClick={() => navigate("/")}>
          MesaLista
        </h1>

        <nav className="nav-links">
          <NavLink
            to="/"
            className={({ isActive }) =>
              isActive ? "nav-link active-link" : "nav-link"
            }
          >
            Inicio
          </NavLink>

          <NavLink
            to="/restaurants"
            className={({ isActive }) =>
              isActive ? "nav-link active-link" : "nav-link"
            }
          >
            Restaurantes
          </NavLink>

          <NavLink
            to="/orders"
            className={({ isActive }) =>
              isActive ? "nav-link active-link" : "nav-link"
            }
          >
            Órdenes
          </NavLink>

          <NavLink
            to="/reviews"
            className={({ isActive }) =>
              isActive ? "nav-link active-link" : "nav-link"
            }
          >
            Reseñas
          </NavLink>
        </nav>

        <div className="nav-right">
          <button className="btn btn-light" onClick={() => navigate("/cart")}>
            Carrito ({itemCount})
          </button>

          <button className="btn btn-primary" onClick={() => navigate("/cart")}>
            Crear Orden
          </button>
        </div>
      </div>
    </header>
  );
}

export default Navbar;