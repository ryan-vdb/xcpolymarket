const API = import.meta.env.VITE_API_URL;

/* -------------- helpers -------------- */
function authHeaders(): HeadersInit {
  const token = localStorage.getItem("token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function handle(r: Response) {
  if (r.status === 401) {
    localStorage.removeItem("token");
    localStorage.removeItem("username");
    window.location.href = "/signin";
    throw new Error("Unauthorized");
  }
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

/* -------------- auth -------------- */
export async function register(username: string, password: string, starting_points = 50) {
  const r = await fetch(`${API}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" } as HeadersInit,
    body: JSON.stringify({ username, password, starting_points }),
  });
  return handle(r);
}

export async function login(username: string, password: string) {
  const r = await fetch(`${API}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" } as HeadersInit,
    body: JSON.stringify({ username, password }),
  });
  return handle(r);
}

/* -------------- markets -------------- */
export async function getOpenMarkets() {
  const r = await fetch(`${API}/markets?status=open`, {
    headers: { ...authHeaders() } as HeadersInit,
  });
  return handle(r);
}

/* -------------- users (token-based) -------------- */
export async function getMe() {
  const r = await fetch(`${API}/users/me`, {
    headers: { ...authHeaders() } as HeadersInit,
  });
  return handle(r);
}

export async function getMyBets() {
  const r = await fetch(`${API}/users/me/bets`, {
    headers: { ...authHeaders() } as HeadersInit,
  });
  return handle(r);
}

/* -------------- bets -------------- */
export async function placeBet(
  marketId: string,
  body: { side: "YES" | "NO"; amount_points: number }
) {
  const r = await fetch(`${API}/markets/${marketId}/bet`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() } as HeadersInit,
    body: JSON.stringify(body),
  });
  return handle(r);
}

export async function getLeaderboard() {
  const API = import.meta.env.VITE_API_URL;
  const r = await fetch(`${API}/users/leaderboard`, {
    headers: { Authorization: `Bearer ${localStorage.getItem("token") || ""}` },
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function trade(marketId: string, body: { side: "YES"|"NO"; amount_points: number }) {
  const API = import.meta.env.VITE_API_URL;
  const r = await fetch(`${API}/markets/${marketId}/trade`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${localStorage.getItem("token") || ""}`,
    },
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json(); // { ok, filled_shares, new_price_yes, new_balance_points }
}

export async function getMyPositions() {
  const API = import.meta.env.VITE_API_URL;
  const r = await fetch(`${API}/users/me/positions`, {
    headers: { Authorization: `Bearer ${localStorage.getItem("token") || ""}` },
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

/* ---------------- admin helpers ---------------- */
function adminHeaders(): HeadersInit {
  const t = localStorage.getItem("adminToken") || "";
  return t ? { "X-Admin-Token": t } : {};
}

export async function adminListUsers() {
  const API = import.meta.env.VITE_API_URL;
  const r = await fetch(`${API}/admin/users`, { headers: adminHeaders() });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function adminListMarkets(status?: "open" | "closed") {
  const API = import.meta.env.VITE_API_URL;
  const qs = status ? `?status=${status}` : "";
  const r = await fetch(`${API}/admin/markets${qs}`, { headers: adminHeaders() });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function adminCloseMarket(marketId: string) {
  const API = import.meta.env.VITE_API_URL;
  const r = await fetch(`${API}/admin/markets/${marketId}/close`, {
    method: "POST",
    headers: adminHeaders(),
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function adminSettleMarket(marketId: string, winner: "YES" | "NO") {
  const API = import.meta.env.VITE_API_URL;
  const r = await fetch(`${API}/admin/markets/${marketId}/settle`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...adminHeaders() },
    body: JSON.stringify({ winner }),
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function adminCreateMarket(body: {
  question: string;
  closes_at: string; // ISO string
  seed_yes_points: number;
  seed_no_points: number;
}) {
  const API = import.meta.env.VITE_API_URL;
  const r = await fetch(`${API}/markets`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...adminHeaders() },
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function adminDeleteMarket(marketId: string) {
  const API = import.meta.env.VITE_API_URL;
  const r = await fetch(`${API}/admin/markets/${marketId}`, {
    method: "DELETE",
    headers: { "X-Admin-Token": localStorage.getItem("adminToken") || "" },
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}