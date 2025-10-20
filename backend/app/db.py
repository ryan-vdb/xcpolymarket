import sqlite3
from contextlib import contextmanager
from .config import DB_PATH

@contextmanager
def conn():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    try:
        yield con
        con.commit()
    except:
        con.rollback()
        raise
    finally:
        con.close()

def init_db():
    with conn() as c:
        c.executescript("""
        PRAGMA journal_mode=WAL;
        CREATE TABLE IF NOT EXISTS users(
          username TEXT PRIMARY KEY,
          balance_cents INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS markets(
          id TEXT PRIMARY KEY,
          question TEXT NOT NULL,
          closes_at TEXT NOT NULL,
          open INTEGER NOT NULL DEFAULT 1,
          s_yes_cents INTEGER NOT NULL,
          s_no_cents INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS bets(
          id TEXT PRIMARY KEY,
          market_id TEXT NOT NULL,
          username TEXT NOT NULL,
          side TEXT NOT NULL CHECK (side IN ('YES','NO')),
          amount_cents INTEGER NOT NULL,
          created_at TEXT NOT NULL,
          UNIQUE (market_id, username, side)
        );
        """)