import { useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { useCart } from "../context/CartContext";

const DB_LINKS = [
  { to: "/admin", label: "Admin CRUD" },
  { to: "/arrays", label: "Arrays" },
  { to: "/transactions", label: "Transacciones" },
  { to: "/gridfs", label: "GridFS" },
  { to: "/indices", label: "Índices" },
];

function Navbar() {
  const navigate = useNavigate();
  const { itemCount } = useCart();
  const [dbOpen, setDbOpen] = useState(false);

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

          <NavLink
            to="/reports"
            className={({ isActive }) =>
              isActive ? "nav-link active-link" : "nav-link"
            }
          >
            Reportes
          </NavLink>

          {/* DB Demo dropdown */}
          <div
            className="nav-dropdown"
            onMouseEnter={() => setDbOpen(true)}
            onMouseLeave={() => setDbOpen(false)}
          >
            <button className="nav-link nav-dropdown-btn">
              DB Demo ▾
            </button>
            {dbOpen && (
              <div className="dropdown-menu">
                {DB_LINKS.map((link) => (
                  <NavLink
                    key={link.to}
                    to={link.to}
                    className={({ isActive }) =>
                      isActive ? "dropdown-item active-link" : "dropdown-item"
                    }
                    onClick={() => setDbOpen(false)}
                  >
                    {link.label}
                  </NavLink>
                ))}
              </div>
            )}
          </div>
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
