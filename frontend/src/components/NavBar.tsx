import { Link } from "react-router-dom";
import { useEffect, useState } from "react";
import { isAdmin } from "../lib/authz";
import { getUsername, isLoggedIn, logout } from "../lib/auth";

export default function NavBar() {
  const [username, setUsername] = useState<string | null>(getUsername());

  useEffect(() => {
    const update = () => setUsername(getUsername());
    // listen for both our custom "auth" event and cross-tab "storage"
    window.addEventListener("auth", update);
    window.addEventListener("storage", update);
    return () => {
      window.removeEventListener("auth", update);
      window.removeEventListener("storage", update);
    };
  }, []);

  if (!isLoggedIn()) return null;

  return (
    <div style={{ display: "flex", gap: 12, padding: 12, borderBottom: "1px solid #eee" }}>
      <Link to="/markets">Markets</Link>
      <Link to="/account">Account</Link>
      <Link to="/leaderboard">Leaderboard</Link>
      {isAdmin(username) && <Link to="/admin">Admin Tools</Link>}
      <div style={{ marginLeft: "auto" }}>
        <span style={{ marginRight: 8 }}>Hi, {username}</span>
        <button onClick={logout}>Log out</button>
      </div>
    </div>
  );
}