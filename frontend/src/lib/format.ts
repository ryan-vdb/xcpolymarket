// frontend/src/lib/format.ts
export function fmtUsd(n: number | string | null | undefined): string {
  const v = typeof n === "string" ? Number(n) : n ?? 0;
  if (Number.isNaN(v)) return "$0.00";
  return v < 0 ? `-$${Math.abs(v).toFixed(2)}` : `$${v.toFixed(2)}`;
}

export function fmtPct(p: number | string | null | undefined): string {
  const v = typeof p === "string" ? Number(p) : p ?? 0;
  if (Number.isNaN(v)) return "0%";
  return `${(v * 100).toFixed(1)}%`;
}

export function plural(n: number, one: string, many?: string) {
  return `${n} ${n === 1 ? one : many ?? one + "s"}`;
}

export function relUntil(iso: string): string {
  const tgt = new Date(iso);
  const now = new Date();
  const ms = tgt.getTime() - now.getTime();
  const sign = ms >= 0 ? 1 : -1;
  const abs = Math.abs(ms);
  const s = Math.round(abs / 1000);
  const m = Math.round(s / 60);
  const h = Math.round(m / 60);
  const d = Math.round(h / 24);

  if (abs < 60_000) return sign > 0 ? `${s}s` : `${s}s ago`;
  if (abs < 3_600_000) return sign > 0 ? `${m}m` : `${m}m ago`;
  if (abs < 86_400_000) return sign > 0 ? `${h}h` : `${h}h ago`;
  return sign > 0 ? `${d}d` : `${d}d ago`;
}

export function absDate(iso: string): string {
  // readable UTC-ish string
  const d = new Date(iso);
  // keep it simple/cross-browser:
  return d.toISOString().replace("T", " ").replace("Z", " UTC");
}