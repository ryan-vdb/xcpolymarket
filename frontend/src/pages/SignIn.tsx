import { useState } from "react";
import { login } from "../lib/api";
import { useNavigate, Link } from "react-router-dom";

export default function SignIn() {
  const [u, setU] = useState(""); 
  const [p, setP] = useState("");
  const [err, setErr] = useState<string|null>(null);
  const nav = useNavigate();

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setErr(null);
    try {
      const res = await login(u, p);
      localStorage.setItem("token", res.access_token);
      localStorage.setItem("username", res.username);
      nav("/markets");
    } catch (e:any) { setErr(String(e)); }
  }

  return (
    <div style={{padding:16}}>
      <h1>Sign in</h1>
      <form onSubmit={submit} style={{display:"grid", gap:8, maxWidth:300}}>
        <input placeholder="username" value={u} onChange={e=>setU(e.target.value)} />
        <input placeholder="password" type="password" value={p} onChange={e=>setP(e.target.value)} />
        <button type="submit">Sign in</button>
      </form>
      {err && <div style={{color:"crimson", marginTop:8}}>{err}</div>}
      <div style={{marginTop:8}}><Link to="/signup">Create an account</Link></div>
    </div>
  );
}