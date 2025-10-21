import { useEffect, useState } from "react";
import { getMe } from "../lib/api";
import { getMyPositions } from "../lib/api";

type Me = { username: string; balance_points: number };
type PositionRow = {
  market_id: string;
  question: string;
  closes_at: string;
  open: boolean;
  price_yes: number;         // 0..1
  yes_shares: number;        // shares (par=1 point-dollar on win)
  no_shares: number;
  est_value_points: number;  // mark-to-market EV in points
};

export default function Account() {
  const [me, setMe] = useState<Me | null>(null);
  const [pos, setPos] = useState<PositionRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    async function run() {
      try {
        const [meRes, posRes] = await Promise.all([getMe(), getMyPositions()]);
        setMe(meRes);
        setPos(posRes);
      } catch (e: any) {
        setErr(String(e));
      } finally {
        setLoading(false);
      }
    }
    run();
  }, []);

  return (
    <div style={{ padding: 16 }}>
      <h1>Account</h1>
      {loading && <div>Loading…</div>}
      {err && <div style={{ color: "crimson" }}>{err}</div>}
      {me && (
        <div style={{ margin: "12px 0", fontSize: 18 }}>
          Balance: <b>{me.balance_points.toLocaleString()}</b> pts
        </div>
      )}

      <h2>Your Markets</h2>
      {pos.length === 0 ? (
        <div>No positions yet.</div>
      ) : (
        <div style={{ display: "grid", gap: 12 }}>
          {pos.map((p) => (
            <div key={p.market_id} style={{ border: "1px solid #eee", padding: 12, borderRadius: 8 }}>
              <div style={{ fontWeight: 600 }}>{p.question}</div>
              <div style={{ fontSize: 12, color: "#666" }}>
                Closes: {p.closes_at} · {p.open ? "Open" : "Closed"}
              </div>
              <div style={{ marginTop: 8, display: "flex", gap: 16, flexWrap: "wrap" }}>
                <div>Price YES: {(p.price_yes * 100).toFixed(1)}%</div>
                <div>YES shares: {p.yes_shares.toLocaleString()}</div>
                <div>NO shares: {p.no_shares.toLocaleString()}</div>
                <div>Est. value: {p.est_value_points.toLocaleString()} pts</div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}