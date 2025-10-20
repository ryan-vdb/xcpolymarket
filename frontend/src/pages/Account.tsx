import { useEffect, useState } from "react";
import { getMe, getMyBets } from "../lib/api";

type BetRow = {
  market_id: string;
  question: string;
  closes_at: string;
  open: boolean;
  side: "YES" | "NO";
  amount_points: number;
  yes_pool_points: number;
  no_pool_points: number;
};

export default function Account() {
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState<string | null>(null);
  const [balance, setBalance] = useState<number | null>(null);
  const [bets, setBets] = useState<BetRow[]>([]);

  useEffect(() => {
    async function load() {
      setLoading(true);
      setErr(null);
      try {
        const me = await getMe();
        setBalance(me.balance_points);
        const bs = await getMyBets();
        setBets(bs);
      } catch (e: any) {
        setErr(e?.message || String(e));
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  return (
    <div style={{ padding: 16 }}>
      <h1>Account</h1>
      {loading && <div>Loading…</div>}
      {err && <div style={{ color: "crimson" }}>Error: {err}</div>}
      {balance != null && (
        <div style={{ fontSize: 24, fontWeight: 700, margin: "8px 0 16px" }}>
          Balance: {balance.toFixed(2)} pts
        </div>
      )}

      <h2>Your Markets</h2>
      {bets.length === 0 && <div>No active bets yet.</div>}
      {bets.map((b) => (
        <div key={b.market_id} style={{ border: "1px solid #ddd", padding: 12, marginTop: 8 }}>
          <div style={{ fontWeight: 600 }}>{b.question}</div>
          <div style={{ fontSize: 12, color: "#666" }}>Closes: {b.closes_at}</div>
          <div style={{ marginTop: 6 }}>
            Your side: <b>{b.side}</b> · Amount: <b>{b.amount_points.toFixed(2)} pts</b>
          </div>
        </div>
      ))}
    </div>
  );
}