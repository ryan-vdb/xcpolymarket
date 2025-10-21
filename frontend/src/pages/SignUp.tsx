import { useState } from "react";
import { register } from "../lib/api";
import { useNavigate, Link } from "react-router-dom";

export default function SignUp() {
  const [u, setU] = useState("");
  const [p, setP] = useState("");
  const [err, setErr] = useState<string|null>(null);
  const nav = useNavigate();

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setErr(null);
    try {
      const res = await register(u, p, 1000); // default 1000 pts
      localStorage.setItem("token", res.access_token);
      localStorage.setItem("username", res.username);
      window.dispatchEvent(new Event("storage"));
      nav("/markets");
    } catch (e:any) { setErr(String(e)); }
  }

  return (
    <div style={{padding:16}}>
      <h1>Create account</h1>
      <form onSubmit={submit} style={{display:"grid", gap:8, maxWidth:300}}>
        <input placeholder="username" value={u} onChange={(e)=>setU(e.target.value)} />
        <input placeholder="password" type="password" value={p} onChange={(e)=>setP(e.target.value)} />
        <button type="submit">Sign up</button>
      </form>
      {err && <div style={{color:"crimson", marginTop:8}}>{err}</div>}
      <div style={{marginTop:8}}><Link to="/signin">Already have an account? Sign in</Link></div>
    </div>
  );
}