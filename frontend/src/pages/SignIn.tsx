import { useState } from "react";
import { login } from "../lib/api";
import { Link } from "react-router-dom";

export default function SignIn() {
  const [u, setU] = useState("");
  const [p, setP] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setErr(null);
    setLoading(true);
    try {
      const res = await login(u, p);
      // fallback to the typed username if backend doesn't return one
      localStorage.setItem("token", res.access_token);
      localStorage.setItem("username", res.username || u);
      window.dispatchEvent(new Event("storage"));
      window.location.replace("/markets");
    } catch (e: any) {
      setErr(String(e?.message || e));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ padding: 16 }}>
      <h1>Sign in</h1>
      <form onSubmit={submit} style={{ display: "grid", gap: 8, maxWidth: 300 }}>
        <input
          placeholder="username"
          value={u}
          onChange={(e) => setU(e.target.value)}
          autoComplete="username"
        />
        <input
          placeholder="password"
          type="password"
          value={p}
          onChange={(e) => setP(e.target.value)}
          autoComplete="current-password"
        />
        <button type="submit" disabled={loading || !u || !p}>
          {loading ? "Signing in…" : "Sign in"}
        </button>
      </form>
      {err && <div style={{ color: "crimson", marginTop: 8 }}>{err}</div>}
      <div style={{ marginTop: 8 }}>
        <Link to="/signup">Create an account</Link>
      </div>
    </div>
  );
}