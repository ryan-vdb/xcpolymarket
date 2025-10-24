// frontend/src/components/MarketCard.tsx
import { fmtUsd, fmtPct, absDate, relUntil } from "../lib/format";

export type Market = {
  id: string;
  question: string;
  closes_at: string;
  open: boolean;
  settled?: boolean;
  winner?: "YES" | "NO" | null;
  yes_pool_points: number; // real cash in YES pool (points == dollars)
  no_pool_points: number;  // real cash in NO  pool
  odds: { yes: number; no: number };
  price_yes: number; // current price of YES (0..1), NO is (1 - price_yes)
  implied_payout_per1_spot?: { yes: number; no: number };
};

export default function MarketCard({
  m,
  onTrade,
}: {
  m: Market;
  onTrade?: (marketId: string) => void;
}) {
  const totalPool = (m.yes_pool_points ?? 0) + (m.no_pool_points ?? 0);
  const priceNo = 1 - (m.price_yes ?? 0);

  const isClosed = !m.open;
  const isSettled = !!m.settled || typeof m.winner === "string";

  return (
    <div style={{
      border: "1px solid #e5e7eb",
      borderRadius: 12,
      padding: 12,
      display: "grid",
      gap: 8,
      background: "#fff",
    }}>
      {/* Question */}
      <div style={{ fontWeight: 600, lineHeight: 1.3 }}>
        {m.question}
      </div>

      {/* Closes / status row */}
      <div style={{ fontSize: 12, color: "#6b7280", display: "flex", gap: 8, alignItems: "baseline" }}>
        <span>Closes: {absDate(m.closes_at)} ({relUntil(m.closes_at)})</span>
        <span style={{ marginLeft: "auto" }}>
          {isSettled ? (
            <Badge color="#065f46" bg="#ecfdf5" text={`Settled · ${m.winner}`} />
          ) : isClosed ? (
            <Badge color="#92400e" bg="#fffbeb" text="Closed" />
          ) : (
            <Badge color="#1f2937" bg="#f3f4f6" text="Open" />
          )}
        </span>
      </div>

      {/* Pricing */}
      <div style={{ display: "flex", gap: 16, flexWrap: "wrap" }}>
        <PricePill label="YES" valueUSD={m.price_yes} percent={m.odds?.yes} />
        <PricePill label="NO" valueUSD={priceNo} percent={m.odds?.no} />
      </div>

      {/* Pool */}
      <div style={{ fontSize: 12, color: "#6b7280" }}>
        Pool: {fmtUsd(totalPool)} (real)
      </div>

      {/* CTA */}
      <div style={{ display: "flex", gap: 8 }}>
        <button
          disabled={isClosed || isSettled}
          onClick={() => onTrade?.(m.id)}
          style={{
            padding: "8px 12px",
            borderRadius: 8,
            border: "1px solid #e5e7eb",
            background: isClosed || isSettled ? "#f9fafb" : "#111827",
            color: isClosed || isSettled ? "#9ca3af" : "#fff",
            cursor: isClosed || isSettled ? "not-allowed" : "pointer",
          }}
        >
          {isSettled ? "Settled" : isClosed ? "Closed" : "Trade"}
        </button>
      </div>
    </div>
  );
}

function PricePill({ label, valueUSD, percent }: { label: string; valueUSD: number; percent: number }) {
  return (
    <div style={{
      display: "flex",
      alignItems: "center",
      gap: 8,
      border: "1px solid #e5e7eb",
      borderRadius: 999,
      padding: "6px 10px",
    }}>
      <span style={{ fontWeight: 600 }}>{label}</span>
      <span style={{ color: "#6b7280" }}>{fmtUsd(valueUSD)}</span>
      <span style={{ fontSize: 12, color: "#6b7280" }}>{fmtPct(percent)}</span>
    </div>
  );
}

function Badge({ text, color, bg }: { text: string; color: string; bg: string }) {
  return (
    <span style={{
      fontSize: 12,
      padding: "2px 8px",
      borderRadius: 999,
      color,
      background: bg,
      border: "1px solid transparent"
    }}>
      {text}
    </span>
  );
}