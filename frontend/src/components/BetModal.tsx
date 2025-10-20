import { useState } from "react";
import { placeBet } from "../lib/api";

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
      const res = await placeBet(marketId, { side, amount_points: amount });
      setStatus(`✅ Bet placed successfully! New balance: ${(res.new_balance_cents / 100).toFixed(2)} pts`);
    } catch (err: any) {
      setStatus(`❌ ${err.message || "Failed to place bet"}`);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div
      style={{
        position: "fixed",
        top: 0, left: 0, width: "100vw", height: "100vh",
        backgroundColor: "rgba(0,0,0,0.5)",
        display: "flex", justifyContent: "center", alignItems: "center",
        zIndex: 1000,
      }}
    >
      <div style={{ background: "white", padding: 20, borderRadius: 8, width: 320 }}>
        <h2>Place Bet</h2>
        <form onSubmit={submit} style={{ display: "grid", gap: 8 }}>
          <label>
            Option:
            <select value={side} onChange={(e) => setSide(e.target.value as "YES" | "NO")}>
              <option value="YES">YES</option>
              <option value="NO">NO</option>
            </select>
          </label>

          <label>
            Amount:
            <input
              type="number"
              value={amount}
              onChange={(e) => setAmount(Number(e.target.value))}
              min={1}
            />
          </label>

          <button type="submit" disabled={loading || amount <= 0}>
            {loading ? "Placing..." : "Submit Bet"}
          </button>
          <button type="button" onClick={onClose} style={{ marginTop: 8 }}>
            Cancel
          </button>
        </form>

        {status && (
          <div style={{ marginTop: 12, fontSize: 14 }}>
            {status}
          </div>
        )}
      </div>
    </div>
  );
}