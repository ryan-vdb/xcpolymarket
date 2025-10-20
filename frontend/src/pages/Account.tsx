import { useEffect, useState } from "react";
import { getUser, getUserBets } from "../lib/api";
import BetModal from "../components/BetModal";

const USERNAME = "alice"; // TODO: replace with real auth later

export default function Account() {
  const [balance, setBalance] = useState<number | null>(null);
  const [bets, setBets] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState<string | null>(null);
  const [activeMarket, setActiveMarket] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const [u, b] = await Promise.all([
          getUser(USERNAME),
          getUserBets(USERNAME),
        ]);
        setBalance(u.balance_points);
        setBets(b);
      } catch (e: any) {
        setErr(String(e));
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  return (
    <div style={{ padding: 16, fontFamily: "system-ui, Arial" }}>
      <h1>Account</h1>
      {loading && <div>Loading…</div>}
      {err && <div style={{ color: "crimson" }}>{err}</div>}
      {balance !== null && (
        <div style={{ fontSize: 36, fontWeight: 800, margin: "8px 0 16px" }}>
          Balance: {balance.toFixed(2)} points
        </div>
      )}

      <h2>Your Markets</h2>
      {bets.length === 0 && !loading && <div>No active bets yet.</div>}
      <div>
        {bets.map((b) => (
          <div
            key={`${b.market_id}-${b.side}`}
            style={{ border: "1px solid #ddd", padding: 12, margin: "12px 0" }}
          >
            <div style={{ fontWeight: 600 }}>{b.question}</div>
            <div style={{ fontSize: 12, color: "#666" }}>
              Closes: {b.closes_at} · Status: {b.open ? "OPEN" : "CLOSED"}
            </div>
            <div style={{ marginTop: 8, display: "flex", gap: 16 }}>
              <div>Your side: {b.side}</div>
              <div>Your amount: {b.amount_points.toFixed(2)}</div>
              <div>
                Current odds — YES: {(b.odds.yes * 100).toFixed(1)}% · NO:{" "}
                {(b.odds.no * 100).toFixed(1)}%
              </div>
              <div>
                Implied payout/1 — YES: {b.implied_payout_per1.yes.toFixed(2)}× ·
                NO: {b.implied_payout_per1.no.toFixed(2)}×
              </div>
            </div>
            {b.open && (
              <button
                style={{ marginTop: 8 }}
                onClick={() => setActiveMarket(b.market_id)}
              >
                Edit Bet
              </button>
            )}
          </div>
        ))}
      </div>

      {activeMarket && (
        <BetModal
          marketId={activeMarket}
          username={USERNAME}
          onClose={() => setActiveMarket(null)}
        />
      )}
    </div>
  );
}