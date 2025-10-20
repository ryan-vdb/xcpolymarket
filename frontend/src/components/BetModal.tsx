import { useState } from "react";
import { placeBet } from "../lib/api";

interface BetModalProps {
  marketId: string;
  username: string;
  onClose: () => void;
}

export default function BetModal({ marketId, username, onClose }: BetModalProps) {
  const [side, setSide] = useState<"YES" | "NO">("YES");
  const [amount, setAmount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const submit = async () => {
    if (!amount) return;
    setLoading(true);
    try {
      const res = await placeBet(marketId, { username, side, amount_points: amount });
      setMessage(`✅ Bet placed! New pools: YES ${res.yes_pool}, NO ${res.no_pool}`);
    } catch (err: any) {
      setMessage("❌ Error placing bet: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      position:"fixed", top:0, left:0, right:0, bottom:0,
      background:"rgba(0,0,0,0.3)", display:"flex", justifyContent:"center", alignItems:"center"
    }}>
      <div style={{background:"white", padding:20, borderRadius:8, width:300}}>
        <h3>Place a Bet</h3>
        <div style={{marginBottom:8}}>
          <label>
            Side:{" "}
            <select value={side} onChange={e => setSide(e.target.value as "YES"|"NO")}>
              <option value="YES">YES</option>
              <option value="NO">NO</option>
            </select>
          </label>
        </div>
        <div style={{marginBottom:8}}>
          <label>
            Amount:{" "}
            <input type="number" value={amount} onChange={e => setAmount(Number(e.target.value))} />
          </label>
        </div>
        <div style={{display:"flex", justifyContent:"space-between", marginTop:12}}>
          <button onClick={submit} disabled={loading}>Place Bet</button>
          <button onClick={onClose}>Close</button>
        </div>
        {message && <div style={{marginTop:12}}>{message}</div>}
      </div>
    </div>
  );
}