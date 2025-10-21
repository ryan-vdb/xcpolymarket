import { useState } from "react";
import { trade } from "../lib/api";

interface BetModalProps {
  marketId: string;
  onClose: () => void;
}

export default function BetModal({ marketId, onClose }: BetModalProps) {
  const [side, setSide] = useState<"YES" | "NO">("YES");
  const [amount, setAmount] = useState<number>(0);
  const [status, setStatus] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setStatus(null);
    setLoading(true);
    try {
      const res = await trade(marketId, { side, amount_points: amount });
      const newBal = (res.new_balance_points ?? res.new_balance_cents / 100).toFixed(2);
      setStatus(`✅ Bet placed! New balance: ${newBal}`);
    } catch (err: any) {
      setStatus(`❌ ${err.message || "Failed to place bet"}`);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div
      style={{
        position: "fixed", inset: 0, background: "rgba(0,0,0,0.5)",
        display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1000
      }}
    >
      <div style={{ background: "#fff", padding: 20, borderRadius: 8, width: 320 }}>
        <h2>Place Bet</h2>
        <form onSubmit={submit} style={{ display: "grid", gap: 8 }}>
          <label>
            Option:&nbsp;
            <select value={side} onChange={(e) => setSide(e.target.value as "YES" | "NO")}>
              <option value="YES">YES</option>
              <option value="NO">NO</option>
            </select>
          </label>
          <label>
            Amount:&nbsp;
            <input type="number" min={1} value={amount} onChange={(e) => setAmount(Number(e.target.value))} />
          </label>
          <button type="submit" disabled={loading || amount <= 0}>{loading ? "Placing..." : "Submit Bet"}</button>
          <button type="button" onClick={onClose}>Cancel</button>
        </form>
        {status && <div style={{ marginTop: 10 }}>{status}</div>}
      </div>
    </div>
  );
}