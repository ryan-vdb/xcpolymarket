import os, sqlite3
from contextlib import contextmanager

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # .../backend/app
DB_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "app.db"))

def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@contextmanager
def conn():
    c = _connect()
    try:
        yield c
        c.commit()
    finally:
        c.close()