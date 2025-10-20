import { useState } from "react";
import { register } from "../lib/api";

export default function SignUp() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const [ok, setOk] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setErr(null);
    setOk(null);
    setLoading(true);
    try {
      const res = await register(username, password);
      // after register, backend typically returns the same token payload as login;
      // if yours returns just {"ok":true}, then redirect to /signin
      if (res.access_token) {
        localStorage.setItem("token", res.access_token);
        localStorage.setItem("username", res.username || username);
        window.location.href = "/account";
      } else {
        setOk("Account created. Please sign in.");
        setTimeout(() => (window.location.href = "/signin"), 800);
      }
    } catch (e: any) {
      setErr(e?.message || "Signup failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ padding: 16 }}>
      <h1>Sign Up</h1>
      <form onSubmit={submit} style={{ display: "grid", gap: 8, maxWidth: 320 }}>
        <input placeholder="Username" value={username} onChange={e=>setUsername(e.target.value)} />
        <input placeholder="Password" type="password" value={password} onChange={e=>setPassword(e.target.value)} />
        <button type="submit" disabled={loading || !username || !password}>
          {loading ? "Creating..." : "Create Account"}
        </button>
        {err && <div style={{ color: "crimson" }}>{err}</div>}
        {ok && <div style={{ color: "green" }}>{ok}</div>}
      </form>
    </div>
  );
}