"""
Persistent storage for ledger proofs (SQLite).
"""
import sqlite3
import json
import os

DB_PATH = "proofs.sqlite"


def init_db():
    """Initialize the proofs database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS proofs (
            run_id TEXT PRIMARY KEY,
            json TEXT NOT NULL,
            sha256 TEXT,
            timestamp REAL,
            agdp_eur REAL,
            pflops REAL,
            agent_net_eur REAL
        )
    """)
    conn.commit()
    conn.close()


def save_ledger(run_id: str, payload: dict):
    """
    Save a ledger proof to SQLite.
    payload should be a dict with keys like:
    - run_id, sha256, timestamp, agdp_eur, total_pflops, agent_net_eur, etc.
    """
    init_db()

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Extract key fields for indexing
    sha256 = payload.get("sha256", "")
    timestamp = payload.get("timestamp", 0.0)
    agdp_eur = payload.get("agdp_eur", 0.0)
    pflops = payload.get("total_pflops", 0.0)
    agent_net_eur = payload.get("agent_net_eur", 0.0)

    c.execute("""
        INSERT OR REPLACE INTO proofs
        (run_id, json, sha256, timestamp, agdp_eur, pflops, agent_net_eur)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        run_id,
        json.dumps(payload, indent=2),
        sha256,
        timestamp,
        agdp_eur,
        pflops,
        agent_net_eur
    ))

    conn.commit()
    conn.close()

    return {"saved": True, "run_id": run_id, "db_path": DB_PATH}


def load_ledger(run_id: str):
    """Load a ledger proof from SQLite by run_id."""
    if not os.path.exists(DB_PATH):
        return None

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT json FROM proofs WHERE run_id = ?", (run_id,))
    row = c.fetchone()
    conn.close()

    if row:
        return json.loads(row[0])
    return None


def list_ledgers(limit=10):
    """List recent ledgers."""
    if not os.path.exists(DB_PATH):
        return []

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        SELECT run_id, timestamp, agdp_eur, pflops, agent_net_eur, sha256
        FROM proofs
        ORDER BY timestamp DESC
        LIMIT ?
    """, (limit,))

    rows = c.fetchall()
    conn.close()

    return [
        {
            "run_id": r[0],
            "timestamp": r[1],
            "agdp_eur": r[2],
            "pflops": r[3],
            "agent_net_eur": r[4],
            "sha256": r[5]
        }
        for r in rows
    ]
