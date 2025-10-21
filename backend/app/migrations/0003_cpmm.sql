-- backend/app/migrations/0003_cpmm.sql

-- Positions: per-user share balances for each market (YES/NO shares).
-- Shares are stored in "cents of par" to stay in integer math.
-- 1 share (par) settles to 100 cents (= 1 point-dollar) on win.
CREATE TABLE IF NOT EXISTS positions (
  id TEXT PRIMARY KEY,
  market_id TEXT NOT NULL,
  username TEXT NOT NULL,
  yes_shares_cents INTEGER NOT NULL DEFAULT 0,
  no_shares_cents  INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL,
  UNIQUE(market_id, username),
  FOREIGN KEY(market_id) REFERENCES markets(id) ON DELETE CASCADE,
  FOREIGN KEY(username)  REFERENCES users(username) ON DELETE CASCADE
);