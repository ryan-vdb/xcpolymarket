import { BrowserRouter, Routes, Route, Link, Navigate } from "react-router-dom";
import { useEffect, useState } from "react";
import Markets from "./pages/Markets";
import Account from "./pages/Account";
import SignIn from "./pages/SignIn";
// If you already have SignUp, keep its import; otherwise comment it out:
// import SignUp from "./pages/SignUp";

function Protected({ children }: { children: React.ReactElement }) {
  // Only check for token presence. Our fetch helpers will auto-logout on 401.
  const token = localStorage.getItem("token");
  if (!token) return <Navigate to="/signin" replace />;
  return children;
}

function Nav() {
  const [username, setUsername] = useState<string | null>(localStorage.getItem("username"));

  useEffect(() => {
    const onStorage = () => setUsername(localStorage.getItem("username"));
    window.addEventListener("storage", onStorage);
    return () => window.removeEventListener("storage", onStorage);
  }, []);

  return (
    <div style={{ display: "flex", gap: 12, padding: 12, borderBottom: "1px solid #eee" }}>
      <Link to="/">Home</Link>
      <Link to="/markets">Markets</Link>
      <Link to="/account">Account</Link>
      <div style={{ marginLeft: "auto" }}>
        {username ? (
          <>
            <span style={{ marginRight: 8 }}>Hi, {username}</span>
            <button
              onClick={() => {
                localStorage.removeItem("token");
                localStorage.removeItem("username");
                window.location.href = "/signin";
              }}
            >
              Logout
            </button>
          </>
        ) : (
          <>
            <Link to="/signin">Sign in</Link>
            {/* If you have SignUp, show it too:
            <span> · </span>
            <Link to="/signup">Sign up</Link>
            */}
          </>
        )}
      </div>
    </div>
  );
}

function Home() {
  return <div style={{ padding: 16 }}>Welcome! Go to Markets or Account.</div>;
}

export default function App() {
  return (
    <BrowserRouter>
      <Nav />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/signin" element={<SignIn />} />
        {/* Uncomment if you have SignUp:
        <Route path="/signup" element={<SignUp />} />
        */}
        <Route path="/markets" element={<Protected><Markets /></Protected>} />
        <Route path="/account" element={<Protected><Account /></Protected>} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}