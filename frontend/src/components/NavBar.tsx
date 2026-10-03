import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../AuthContext";
import { useSearchResults } from "../SearchResultsContext";

export default function NavBar() {
  const { user, logout } = useAuth();
  const { clearResults } = useSearchResults();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/");
  }

  return (
    <nav className="navbar">
      <div className="navbar-brand">Campus Customs</div>
      <ul className="navbar-links">
        <li>
          <NavLink to="/" end className={({ isActive }) => (isActive ? "active" : "")}>
            Home
          </NavLink>
        </li>
        <li>
          <NavLink
            to="/products"
            onClick={clearResults}
            className={({ isActive }) => (isActive ? "active" : "")}
          >
            Products
          </NavLink>
        </li>
        <li>
          <NavLink to="/about" className={({ isActive }) => (isActive ? "active" : "")}>
            About Us
          </NavLink>
        </li>
        {user ? (
          <>
            <li>Hi, {user.first_name ?? user.name}</li>
            <li>
              <button className="navbar-cta" onClick={handleLogout}>
                Log Out
              </button>
            </li>
          </>
        ) : (
          <>
            <li>
              <NavLink to="/login" className={({ isActive }) => (isActive ? "active" : "")}>
                Log In
              </NavLink>
            </li>
            <li>
              <NavLink to="/create-account" className="navbar-cta">
                Create Account
              </NavLink>
            </li>
          </>
        )}
      </ul>
    </nav>
  );
}
