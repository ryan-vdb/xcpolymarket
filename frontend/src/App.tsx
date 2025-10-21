import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Markets from "./pages/Markets";
import Account from "./pages/Account";
import Leaderboard from "./pages/Leaderboard";
import AdminTools from "./pages/AdminTools";
import SignIn from "./pages/SignIn";
import NavBar from "./components/NavBar";
import { isLoggedIn, getUsername } from "./lib/auth";
import { isAdmin } from "./lib/authz";

function PrivateRoute({ children }: { children: React.ReactElement }) {
  return isLoggedIn() ? children : <Navigate to="/signin" replace />;
}

function AdminOnly({ children }: { children: React.ReactElement }) {
  const username = getUsername();
  return isAdmin(username) ? children : <Navigate to="/" replace />;
}

export default function App() {
  return (
    <BrowserRouter>
      {/* Always render; NavBar itself hides when logged out */}
      <NavBar />

      <Routes>
        {/* Public */}
        <Route path="/signin" element={<SignIn />} />

        {/* Private */}
        <Route path="/markets" element={<PrivateRoute><Markets /></PrivateRoute>} />
        <Route path="/account" element={<PrivateRoute><Account /></PrivateRoute>} />
        <Route path="/leaderboard" element={<PrivateRoute><Leaderboard /></PrivateRoute>} />
        <Route
          path="/admin"
          element={
            <PrivateRoute>
              <AdminOnly>
                <AdminTools />
              </AdminOnly>
            </PrivateRoute>
          }
        />

        {/* Default redirect (compute fresh each render) */}
        <Route path="*" element={<Navigate to={isLoggedIn() ? "/markets" : "/signin"} replace />} />
      </Routes>
    </BrowserRouter>
  );
}