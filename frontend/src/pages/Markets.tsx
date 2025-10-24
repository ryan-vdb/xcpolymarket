// frontend/src/pages/Markets.tsx
import { useEffect, useState } from "react";
import { getOpenMarkets } from "../lib/api";
import MarketCard, { type Market } from "../components/MarketCard";
import BetModal from "../components/BetModal";

export default function Markets() {
  const [markets, setMarkets] = useState<Market[]>([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState<string | null>(null);
  const [activeMarket, setActiveMarket] = useState<string | null>(null);

  async function load() {
    try {
      setErr(null);
      setLoading(true);
      const data = await getOpenMarkets();
      setMarkets(data);
    } catch (e: any) {
      setErr(String(e?.message || e));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  return (
    <div style={{ padding: 16, display: "grid", gap: 12 }}>
      <h1 style={{ margin: 0 }}>Markets</h1>
      {loading && <div>Loading…</div>}
      {err && <div style={{ color: "crimson" }}>{err}</div>}
      {!loading && markets.length === 0 && <div>No live markets. Check back soon.</div>}

      {markets.map((m) => (
        <MarketCard key={m.id} m={m} onTrade={(id) => setActiveMarket(id)} />
      ))}

      {activeMarket && (
        <BetModal
          marketId={activeMarket}
          onClose={() => setActiveMarket(null)}
          onDone={() => load()}
        />
      )}
    </div>
  );
}