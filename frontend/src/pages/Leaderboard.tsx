import { useEffect, useState } from "react";
import { getLeaderboard } from "../lib/api";

type Row = { username: string; balance_points: number };

export default function Leaderboard() {
  const [rows, setRows] = useState<Row[]>([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    getLeaderboard()
      .then(setRows)
      .catch(e => setErr(String(e)))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div style={{ padding: 16 }}>
      <h1>Leaderboard</h1>
      {loading && <div>Loading…</div>}
      {err && <div style={{ color: "crimson" }}>{err}</div>}
      {!loading && !err && (
        <ol style={{ paddingLeft: 20 }}>
          {rows.map(r => (
            <li key={r.username} style={{ margin: "6px 0" }}>
              <b>{r.username}</b> — {r.balance_points.toLocaleString()} pts
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}