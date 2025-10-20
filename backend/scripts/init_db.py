# backend/scripts/init_db.py
import os, sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))            # .../backend/scripts
DB_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "app.db"))  # .../backend/app.db

DDL = """
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS users (
  username TEXT PRIMARY KEY,
  balance_cents INTEGER NOT NULL,
  password_hash TEXT
);

CREATE TABLE IF NOT EXISTS markets (
  id TEXT PRIMARY KEY,
  question TEXT NOT NULL,
  closes_at TEXT NOT NULL,
  open INTEGER NOT NULL DEFAULT 1,
  s_yes_cents INTEGER NOT NULL DEFAULT 0,
  s_no_cents  INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS bets (
  id TEXT PRIMARY KEY,
  market_id TEXT NOT NULL,
  username TEXT NOT NULL,
  side TEXT NOT NULL CHECK (side IN ('YES','NO')),
  amount_cents INTEGER NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY (market_id) REFERENCES markets(id) ON DELETE CASCADE,
  FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
);
"""

def main():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.executescript(DDL)
        conn.commit()
        print(f"✅ Initialized DB at {DB_PATH}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()