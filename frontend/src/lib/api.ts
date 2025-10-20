const API = import.meta.env.VITE_API_URL;

/* ---------- AUTH ---------- */

export async function register(username: string, password: string, starting_points = 1000) {
  const r = await fetch(`${API}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" } as HeadersInit,
    body: JSON.stringify({ username, password, starting_points }),
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function login(username: string, password: string) {
  const r = await fetch(`${API}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" } as HeadersInit,
    body: JSON.stringify({ username, password }),
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export function authHeaders(): HeadersInit {
  const token = localStorage.getItem("token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

/* ---------- MARKETS ---------- */

export async function getOpenMarkets() {
  const r = await fetch(`${API}/markets?status=open`, {
    headers: { ...authHeaders() } as HeadersInit,
  });
  if (!r.ok) throw new Error("Failed to fetch markets");
  return r.json();
}

/* ---------- USERS ---------- */

export async function getUser(username: string) {
  const r = await fetch(`${API}/users/${encodeURIComponent(username)}`, {
    headers: { ...authHeaders() } as HeadersInit,
  });
  if (!r.ok) throw new Error("User not found");
  return r.json();
}

export async function getUserBets(username: string) {
  const r = await fetch(`${API}/users/${encodeURIComponent(username)}/bets`, {
    headers: { ...authHeaders() } as HeadersInit,
  });
  if (!r.ok) throw new Error("Failed to fetch user bets");
  return r.json();
}

/* ---------- BETS ---------- */

export async function placeBet(
  marketId: string,
  body: { side: "YES" | "NO"; amount_points: number }
) {
  const r = await fetch(`${API}/markets/${marketId}/bet`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() } as HeadersInit,
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}