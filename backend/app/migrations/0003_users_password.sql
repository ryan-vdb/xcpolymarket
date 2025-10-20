ALTER TABLE users ADD COLUMN password_hash TEXT;
ALTER TABLE users ADD COLUMN created_at TEXT DEFAULT (datetime('now'));