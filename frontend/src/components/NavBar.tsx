import { Link } from "react-router-dom";
import { isLoggedIn, getUsername, logout } from "../lib/auth";

export default function NavBar() {
  if (!isLoggedIn()) return null; // never show when logged out

  const user = getUsername();
  return (
    <div style={{ display: "flex", gap: 12, padding: 12, borderBottom: "1px solid #eee" }}>
      <Link to="/markets">Markets</Link>
      <Link to="/account">Account</Link>
      <Link to="/leaderboard">Leaderboard</Link>
      <div style={{ marginLeft: "auto" }}>
        <span style={{ marginRight: 8 }}>Hi, {user}</span>
        <button onClick={logout}>Log out</button>
      </div>
    </div>
  );
}