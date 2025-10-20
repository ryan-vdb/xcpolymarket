const API = import.meta.env.VITE_API_URL;

export async function getOpenMarkets() {
  const r = await fetch(`${API}/markets?status=open`);
  if (!r.ok) throw new Error("Failed to fetch markets");
  return r.json();
}

export async function getUser(username: string) {
  const r = await fetch(`${API}/users/${encodeURIComponent(username)}`);
  if (!r.ok) throw new Error("User not found");
  return r.json();
}

export async function placeBet(marketId: string, body: {username:string; side:'YES'|'NO'; amount_points:number}) {
  const r = await fetch(`${API}/markets/${marketId}/bet`, {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify(body)
  });
  if (!r.ok) throw new Error("Bet failed");
  return r.json();
}

export async function getUserBets(username: string) {
  const API = import.meta.env.VITE_API_URL;
  const r = await fetch(`${API}/users/${encodeURIComponent(username)}/bets`);
  if (!r.ok) throw new Error("Failed to fetch user bets");
  return r.json();
}