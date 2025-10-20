import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import Markets from "./pages/Markets";
import Account from "./pages/Account";

export default function App() {
  return (
    <BrowserRouter>
      <nav style={{display:'flex', gap:12, padding:12, borderBottom:'1px solid #ddd'}}>
        <Link to="/markets">Markets</Link>
        <Link to="/account">Account</Link>
      </nav>
      <Routes>
        <Route path="/markets" element={<Markets />} />
        <Route path="/account" element={<Account />} />
        <Route path="*" element={<Markets />} />
      </Routes>
    </BrowserRouter>
  );
}