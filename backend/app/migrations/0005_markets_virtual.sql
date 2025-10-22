-- 0005_markets_virtual.sql
-- Add CPMM columns to markets: real pools + virtual liquidity + settle flags.

-- NOTE: SQLite doesn't support IF NOT EXISTS with ADD COLUMN in older versions.
-- If a column already exists, running this file will error on that statement.
-- In dev, it's OK to run once on a fresh DB. If you re-run, ignore duplicate errors.

ALTER TABLE markets ADD COLUMN yes_real_cents INTEGER NOT NULL DEFAULT 0;
ALTER TABLE markets ADD COLUMN no_real_cents  INTEGER NOT NULL DEFAULT 0;

ALTER TABLE markets ADD COLUMN virt_yes_cents INTEGER NOT NULL DEFAULT 100000; -- = 1000 points depth
ALTER TABLE markets ADD COLUMN virt_no_cents  INTEGER NOT NULL DEFAULT 100000;

-- Optional but recommended: settle bookkeeping to prevent double payouts
ALTER TABLE markets ADD COLUMN settled INTEGER NOT NULL DEFAULT 0;             -- 0=open/closed, 1=settled
ALTER TABLE markets ADD COLUMN winner  TEXT CHECK(winner IN ('YES','NO'));     -- NULL until settled

-- If you had old pool columns (e.g., s_yes_cents/s_no_cents), migrate their values into the new real pools.
-- These UPDATEs are harmless if the old columns don't exist (they'll simply fail). Run once on a DB that has them.
-- If your SQLite errors here because the old columns don't exist, you can safely comment these two lines.

UPDATE markets SET yes_real_cents = COALESCE(s_yes_cents, 0) WHERE 1=1;
UPDATE markets SET no_real_cents  = COALESCE(s_no_cents,  0) WHERE 1=1;