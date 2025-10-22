-- 0004_positions.sql
-- Tracks aggregate user positions (shares) per market.
-- Each 1.0 share pays 1 point (= 100 cents) if that side wins.

CREATE TABLE IF NOT EXISTS positions(
  market_id TEXT NOT NULL,
  username  TEXT NOT NULL,
  yes_shares_points REAL NOT NULL DEFAULT 0.0,
  no_shares_points  REAL NOT NULL DEFAULT 0.0,
  PRIMARY KEY (market_id, username)
);