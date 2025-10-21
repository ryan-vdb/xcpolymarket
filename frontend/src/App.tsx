import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Markets from "./pages/Markets";
import Account from "./pages/Account";
import Leaderboard from "./pages/Leaderboard";
import SignIn from "./pages/SignIn";
import NavBar from "./components/NavBar";
import { isLoggedIn } from "./lib/auth";

function PrivateRoute({ children }: { children: React.ReactElement }) {
  return isLoggedIn() ? children : <Navigate to="/signin" replace />;
}

export default function App() {
  const authed = isLoggedIn();

  return (
    <BrowserRouter>
      {/* Only show the nav bar when authenticated */}
      {authed && <NavBar />}

      <Routes>
        {/* Sign in is the only public route */}
        <Route path="/signin" element={<SignIn />} />

        {/* Everything else is gated */}
        <Route path="/markets" element={<PrivateRoute><Markets /></PrivateRoute>} />
        <Route path="/account" element={<PrivateRoute><Account /></PrivateRoute>} />
        <Route path="/leaderboard" element={<Leaderboard />} />

        {/* Default: if authed go to markets, else go to sign in */}
        <Route path="*" element={<Navigate to={authed ? "/markets" : "/signin"} replace />} />
      </Routes>
    </BrowserRouter>
  );
}