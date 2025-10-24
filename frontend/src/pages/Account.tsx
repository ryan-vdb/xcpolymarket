// frontend/src/pages/Account.tsx
import { useEffect, useState } from "react";
import { getMe, getMyBets } from "../lib/api";
import { fmtUsd, absDate } from "../lib/format";

type Me = { username: string; balance_points: number };

type MyBet = {
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
  const [me, setMe] = useState<Me | null>(null);
  const [bets, setBets] = useState<MyBet[]>([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState<string | null>(null);

  async function load() {
    try {
      setErr(null);
      setLoading(true);
      const user = await getMe();          // TOKEN-BASED
      setMe(user);
      const myBets = await getMyBets();    // TOKEN-BASED
      setBets(myBets);
    } catch (e: any) {
      setErr(String(e?.message || e));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  return (
    <div style={{ padding: 16, display: "grid", gap: 12 }}>
      <h1 style={{ margin: 0 }}>Account</h1>

      {loading && <div>Loading…</div>}
      {err && <div style={{ color: "crimson" }}>{err}</div>}

      {me && (
        <div
          style={{
            border: "1px solid #e5e7eb",
            borderRadius: 12,
            padding: 12,
            background: "#fff",
            color: "#111827",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <div>
            <div style={{ fontSize: 12, color: "#6b7280" }}>Signed in as</div>
            <div style={{ fontWeight: 600 }}>{me.username}</div>
          </div>
          <div>
            <div style={{ fontSize: 12, color: "#6b7280", textAlign: "right" }}>Balance</div>
            <div
              style={{
                fontWeight: 700,
                fontSize: 20,
                textAlign: "right",
                color: "#111827",
              }}
            >
              {fmtUsd(me.balance_points)}
            </div>
          </div>
        </div>
      )}

      <h2 style={{ margin: "8px 0 0" }}>Your Positions</h2>
      {(!loading && bets.length === 0) && <div>No active positions yet.</div>}

      <div style={{ display: "grid", gap: 8 }}>
        {bets.map((b, i) => (
          <div
            key={i}
            style={{
              border: "1px solid #e5e7eb",
              borderRadius: 12,
              padding: 12,
              background: "#fff",
              color: "#111827",
              display: "grid",
              gap: 4,
            }}
          >
            <div style={{ fontWeight: 600 }}>{b.question}</div>
            <div style={{ fontSize: 12, color: "#6b7280" }}>
              Closes: {absDate(b.closes_at)} · Side: {b.side}
            </div>
            <div style={{ fontSize: 14 }}>
              Stake: {fmtUsd(b.amount_points)}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}