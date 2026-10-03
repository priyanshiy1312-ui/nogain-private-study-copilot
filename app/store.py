"""SQLite storage + tiny numpy vector search (no external vector DB; swap for Chroma later if desired)."""
import sqlite3, threading
import numpy as np
from . import config

_lock = threading.RLock()
_conn = None
SCHEMA = """
CREATE TABLE IF NOT EXISTS chunks(id INTEGER PRIMARY KEY, course TEXT, source TEXT, idx INT, text TEXT, emb BLOB);
CREATE TABLE IF NOT EXISTS memories(id INTEGER PRIMARY KEY, ts REAL, kind TEXT, text TEXT, emb BLOB);
CREATE TABLE IF NOT EXISTS messages(id INTEGER PRIMARY KEY, ts REAL, session TEXT, role TEXT, content TEXT);
CREATE TABLE IF NOT EXISTS audit(id INTEGER PRIMARY KEY, ts REAL, actor TEXT, tool TEXT, target TEXT, decision TEXT, layer TEXT, detail TEXT);
CREATE TABLE IF NOT EXISTS approvals(id INTEGER PRIMARY KEY, ts REAL, tool TEXT, args TEXT, status TEXT);
CREATE TABLE IF NOT EXISTS briefings(id INTEGER PRIMARY KEY, ts REAL, text TEXT);
CREATE TABLE IF NOT EXISTS applications(id INTEGER PRIMARY KEY, ts REAL, company TEXT, role TEXT, status TEXT, notes TEXT);
CREATE TABLE IF NOT EXISTS outbox(id INTEGER PRIMARY KEY, ts REAL, to_addr TEXT, subject TEXT, body TEXT);
"""


def db():
    global _conn
    with _lock:
        if _conn is None:
            config.HOME.mkdir(parents=True, exist_ok=True)
            _conn = sqlite3.connect(config.DB_PATH, check_same_thread=False)
            _conn.row_factory = sqlite3.Row
            _conn.executescript(SCHEMA)
        return _conn


def execute(sql, args=()):
    with _lock:
        cur = db().execute(sql, args)
        db().commit()
        return cur.lastrowid


def query(sql, args=()):
    with _lock:
        return [dict(r) for r in db().execute(sql, args).fetchall()]


def vec_search(table, qvec, k=4, where="", args=()):
    """Cosine search over rows with an `emb` BLOB (float32, L2-normalised)."""
    rows = query(f"SELECT * FROM {table} {where}", args)
    scored = []
    for r in rows:
        v = np.frombuffer(r["emb"], dtype=np.float32)
        scored.append((float(np.dot(qvec, v)), r))
    scored.sort(key=lambda t: -t[0])
    return [dict(r, score=s) for s, r in scored[:k]]
