// frontend/src/components/BetModal.tsx
import { useEffect, useState } from "react";
import { placeBet } from "../lib/api";
import { fmtUsd } from "../lib/format";

type Side = "YES" | "NO";

export default function BetModal({
  marketId,
  onClose,
  onDone,
}: {
  marketId: string;
  onClose: () => void;
  onDone?: () => void; // optional refresh callback
}) {
  const [side, setSide] = useState<Side>("YES");
  const [amount, setAmount] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  // trap ESC
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setErr(null);
    setLoading(true);
    try {
      const spend_points = Number(amount || 0);
      if (!spend_points || spend_points <= 0) {
        setErr("Enter an amount greater than $0.00");
        setLoading(false);
        return;
      }
      await placeBet(marketId, { side: side, spend_points: Number(amount) });
      onDone?.();
      onClose();
    } catch (e: any) {
      setErr(String(e?.message || e));
    } finally {
      setLoading(false);
    }
  }

  function preset(val: number) {
    setAmount(String(val));
  }

  return (
    <div style={backdrop}>
      <div style={sheet}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
          <h3 style={{ margin: 0 }}>Place Trade</h3>
          <button onClick={onClose} style={xBtn} aria-label="Close">×</button>
        </div>

        <form onSubmit={submit} style={{ display: "grid", gap: 12, marginTop: 12 }}>
          {/* Side picker */}
          <div style={{ display: "flex", gap: 8 }}>
            {(["YES", "NO"] as Side[]).map(s => (
              <button
                key={s}
                type="button"
                onClick={() => setSide(s)}
                style={{
                  padding: "8px 12px",
                  borderRadius: 8,
                  border: "1px solid #e5e7eb",
                  background: side === s ? "#111827" : "#fff",
                  color: side === s ? "#fff" : "#111827",
                  cursor: "pointer",
                }}
              >
                {s}
              </button>
            ))}
          </div>

          {/* Amount */}
          <div>
            <label style={{ display: "block", fontSize: 12, color: "#6b7280", marginBottom: 4 }}>
              Amount (USD)
            </label>
            <input
              inputMode="decimal"
              placeholder="e.g. 10"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              style={inp}
            />
            <div style={{ display: "flex", gap: 8, marginTop: 6 }}>
              {[5, 10, 25].map(v => (
                <button key={v} type="button" onClick={() => preset(v)} style={chip}>
                  {fmtUsd(v)}
                </button>
              ))}
            </div>
          </div>

          {/* Submit */}
          <div style={{ display: "flex", gap: 8 }}>
            <button type="submit" disabled={loading} style={primary}>
              {loading ? "Placing…" : "Confirm trade"}
            </button>
            <button type="button" onClick={onClose} disabled={loading} style={secondary}>
              Cancel
            </button>
          </div>

          {err && <div style={{ color: "crimson", fontSize: 13 }}>{err}</div>}
        </form>
      </div>
    </div>
  );
}

const backdrop: React.CSSProperties = {
  position: "fixed",
  inset: 0,
  background: "rgba(0,0,0,0.35)",
  display: "grid",
  placeItems: "center",
  padding: 16,
  zIndex: 50,
};

const sheet: React.CSSProperties = {
  background: "#fff",
  borderRadius: 12,
  border: "1px solid #e5e7eb",
  width: "100%",
  maxWidth: 420,
  padding: 16,
  boxShadow: "0 10px 30px rgba(0,0,0,0.15)",
};

const xBtn: React.CSSProperties = {
  border: "1px solid #e5e7eb",
  background: "#fff",
  borderRadius: 8,
  width: 32,
  height: 32,
  cursor: "pointer",
};

const inp: React.CSSProperties = {
  width: "100%",
  padding: "10px 12px",
  borderRadius: 8,
  border: "1px solid #e5e7eb",
  fontSize: 14,
};

const chip: React.CSSProperties = {
  padding: "6px 10px",
  borderRadius: 999,
  border: "1px solid #e5e7eb",
  background: "#fff",
  cursor: "pointer",
};

const primary: React.CSSProperties = {
  padding: "10px 12px",
  borderRadius: 8,
  border: "1px solid #111827",
  background: "#111827",
  color: "#fff",
  cursor: "pointer",
};

const secondary: React.CSSProperties = {
  padding: "10px 12px",
  borderRadius: 8,
  border: "1px solid #e5e7eb",
  background: "#fff",
  color: "#111827",
  cursor: "pointer",
};