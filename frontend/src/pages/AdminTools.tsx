import { useEffect, useState } from "react";
import { adminCreateMarket, adminListMarkets, adminCloseMarket, adminSettleMarket, adminListUsers, adminDeleteMarket } from "../lib/api";

type AdminMarket = {
  id: string;
  question: string;
  closes_at: string;
  open: boolean;
  yes_pool_points: number;
  no_pool_points: number;
  odds: { yes: number; no: number };
};

type AdminUser = { username: string; balance_points: number };

export default function AdminTools() {
  const [adminToken, setAdminToken] = useState(localStorage.getItem("adminToken") || "");
  const [status, setStatus] = useState<"" | "open" | "closed">("");
  const [markets, setMarkets] = useState<AdminMarket[]>([]);
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [err, setErr] = useState<string | null>(null);

  // Create market form
  const [q, setQ] = useState("");
  const [closesAt, setClosesAt] = useState(""); // "2025-12-31T23:59:00Z" or local
  const [seedYes, setSeedYes] = useState(500);
  const [seedNo, setSeedNo] = useState(500);

  function saveToken() {
    localStorage.setItem("adminToken", adminToken);
    refresh();
  }
  function clearToken() {
    localStorage.removeItem("adminToken");
    setAdminToken("");
  }

  async function refresh() {
    setErr(null);
    try {
      const [m, u] = await Promise.all([
        adminListMarkets(status || undefined),
        adminListUsers()
      ]);
      setMarkets(m);
      setUsers(u);
    } catch (e: any) {
      setErr(String(e));
    }
  }

  useEffect(() => {
    refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [status]);

  async function doCreateMarket(e: React.FormEvent) {
    e.preventDefault();
    setErr(null);
    try {
      await adminCreateMarket({
        question: q,
        closes_at: closesAt,
        seed_yes_points: seedYes,
        seed_no_points: seedNo,
      });
      setQ("");
      setClosesAt("");
      setSeedYes(500);
      setSeedNo(500);
      refresh();
    } catch (e: any) {
      setErr(String(e));
    }
  }

  async function doClose(id: string) {
    setErr(null);
    try { await adminCloseMarket(id); refresh(); }
    catch (e:any) { setErr(String(e)); }
  }

  async function doSettle(id: string, winner: "YES" | "NO") {
    setErr(null);
    try { await adminSettleMarket(id, winner); refresh(); }
    catch (e:any) { setErr(String(e)); }
  }

  async function doDelete(id: string) {
  setErr(null);
  try {
    const ok = window.confirm("Delete this market permanently? This cannot be undone.");
    if (!ok) return;
    await adminDeleteMarket(id);
    refresh();
  } catch (e: any) {
    setErr(String(e));
  }
}
  return (
    <div style={{ padding: 16, display: "grid", gap: 16 }}>
      <h1>Admin Tools</h1>

      <div style={{ border: "1px solid #eee", padding: 12, borderRadius: 8 }}>
        <h3>Admin token</h3>
        <div style={{ display: "flex", gap: 8 }}>
          <input
            placeholder="paste X-Admin-Token (e.g., dev-admin-token)"
            value={adminToken}
            onChange={(e) => setAdminToken(e.target.value)}
            style={{ flex: 1 }}
          />
          <button onClick={saveToken}>Save</button>
          <button onClick={clearToken}>Clear</button>
        </div>
        <div style={{ fontSize: 12, color: "#666", marginTop: 4 }}>
          This is only stored in your browser (localStorage). Backend still enforces admin.
        </div>
      </div>

      {err && <div style={{ color: "crimson" }}>{err}</div>}

      <div style={{ border: "1px solid #eee", padding: 12, borderRadius: 8 }}>
        <h3>Create market</h3>
        <form onSubmit={doCreateMarket} style={{ display: "grid", gap: 8, maxWidth: 640 }}>
          <input placeholder="Question" value={q} onChange={(e)=>setQ(e.target.value)} required />
          <input
            placeholder="Closes at (ISO e.g. 2025-12-31T23:59:00Z)"
            value={closesAt}
            onChange={(e)=>setClosesAt(e.target.value)}
            required
          />
          <div style={{ display: "flex", gap: 8 }}>
            <label>Seed YES pts <input type="number" value={seedYes} onChange={e=>setSeedYes(Number(e.target.value))} min={0} /></label>
            <label>Seed NO pts <input type="number" value={seedNo} onChange={e=>setSeedNo(Number(e.target.value))} min={0} /></label>
          </div>
          <button type="submit">Create</button>
        </form>
      </div>

      <div style={{ border: "1px solid #eee", padding: 12, borderRadius: 8 }}>
        <h3>Markets</h3>
        <div style={{ marginBottom: 8 }}>
          <label>Filter: </label>
          <select value={status} onChange={e=>setStatus(e.target.value as any)}>
            <option value="">All</option>
            <option value="open">Open</option>
            <option value="closed">Closed</option>
          </select>
          <button style={{ marginLeft: 8 }} onClick={refresh}>Refresh</button>
        </div>
        <div style={{ display: "grid", gap: 8 }}>
          {markets.map(m => (
            <div key={m.id} style={{ border: "1px solid #ddd", padding: 10, borderRadius: 8 }}>
              <div style={{ fontWeight: 600 }}>{m.question}</div>
              <div style={{ fontSize: 12, color: "#666" }}>
                Closes: {m.closes_at} · {m.open ? "Open" : "Closed"}
              </div>
              <div style={{ marginTop: 6 }}>
                YES pool: {m.yes_pool_points.toLocaleString()} · NO pool: {m.no_pool_points.toLocaleString()} ·
                Price YES: {(m.odds.yes * 100).toFixed(1)}%
              </div>
              <div style={{ marginTop: 8, display: "flex", gap: 8 }}>
                {m.open ? (
                  <button onClick={() => doClose(m.id)}>Close trading</button>
                ) : (
                  <>
                    <button onClick={() => doSettle(m.id, "YES")}>Settle YES</button>
                    <button onClick={() => doSettle(m.id, "NO")}>Settle NO</button>
                    <button
                        onClick={() => doDelete(m.id)}
                        style={{ background: "#fff0f0", border: "1px solid #f3b1b1" }}
                        title="Permanently delete this market"
                    >
                        Delete
                    </button>
                  </>
                )}
              </div>
            </div>
          ))}
          {markets.length === 0 && <div>No markets found.</div>}
        </div>
      </div>

      <div style={{ border: "1px solid #eee", padding: 12, borderRadius: 8 }}>
        <h3>Users</h3>
        <ul>
          {users.map(u => (
            <li key={u.username}>
              <b>{u.username}</b> — {u.balance_points.toLocaleString()} pts
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}