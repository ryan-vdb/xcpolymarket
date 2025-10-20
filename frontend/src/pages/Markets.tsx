import { useEffect, useState } from "react";
import { getOpenMarkets } from "../lib/api";
import BetModal from "../components/BetModal";

export default function Markets() {
  const [markets, setMarkets] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState<string | null>(null);
  const [activeMarket, setActiveMarket] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      setLoading(true);
      setErr(null);
      try {
        const m = await getOpenMarkets();
        setMarkets(m);
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
      <h1>Open Markets</h1>
      {loading && <div>Loading…</div>}
      {err && <div style={{ color: "crimson" }}>Error: {err}</div>}
      {markets.map((m) => (
        <div key={m.id} style={{ border: "1px solid #ddd", padding: 12, margin: "12px 0" }}>
          <div style={{ fontWeight: 600 }}>{m.question}</div>
          <div style={{ fontSize: 12, color: "#666" }}>Closes: {m.closes_at}</div>
          <div style={{ marginTop: 8, display: "flex", gap: 16 }}>
            <div>YES: {(m.odds.yes * 100).toFixed(1)}% · pays ~{m.implied_payout_per1.yes.toFixed(2)}x</div>
            <div>NO: {(m.odds.no * 100).toFixed(1)}% · pays ~{m.implied_payout_per1.no.toFixed(2)}x</div>
          </div>
          <button style={{ marginTop: 8 }} onClick={() => setActiveMarket(m.id)}>
            Place/Edit Bet
          </button>
        </div>
      ))}
      {activeMarket && <BetModal marketId={activeMarket} onClose={() => setActiveMarket(null)} />}
    </div>
  );
}