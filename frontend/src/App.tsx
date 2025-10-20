import { BrowserRouter, Routes, Route, Link, Navigate } from "react-router-dom";
import Markets from "./pages/Markets";
import Account from "./pages/Account";
import SignIn from "./pages/SignIn";
import SignUp from "./pages/SignUp";

function Protected({ children }: {children: React.ReactElement}) {
  const token = localStorage.getItem("token");
  return token ? children : <Navigate to="/signin" replace />;
}

export default function App() {
  return (
    <BrowserRouter>
      <nav style={{display:'flex', gap:12, padding:12, borderBottom:'1px solid #ddd'}}>
        <Link to="/markets">Markets</Link>
        <Link to="/account">Account</Link>
        <span style={{marginLeft:"auto"}}>{localStorage.getItem("username") || "guest"}</span>
      </nav>
      <Routes>
        <Route path="/signin" element={<SignIn />} />
        <Route path="/signup" element={<SignUp />} />
        <Route path="/markets" element={<Protected><Markets /></Protected>} />
        <Route path="/account" element={<Protected><Account /></Protected>} />
        <Route path="*" element={<Navigate to="/markets" replace />} />
      </Routes>
    </BrowserRouter>
  );
}