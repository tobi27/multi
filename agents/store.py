import sqlite3, json, time, threading
DB="proofs.sqlite"

# Connection pool thread-safe
_CONN_LOCK = threading.Lock()
_CONN = None

def _get_connection():
    global _CONN
    with _CONN_LOCK:
        if _CONN is None:
            _CONN = sqlite3.connect(DB, check_same_thread=False)
            _CONN.execute("CREATE TABLE IF NOT EXISTS proofs(run_id TEXT PRIMARY KEY, ts INTEGER, json TEXT)")
            _CONN.commit()
        return _CONN

def save_ledger(run_id: str, payload: dict):
    conn = _get_connection()
    with _CONN_LOCK:
        try:
            conn.execute("INSERT OR REPLACE INTO proofs VALUES(?,?,?)",
                        (run_id, int(time.time()), json.dumps(payload)))
            conn.commit()
        except Exception as e:
            print(f"[STORE] Error saving ledger: {e}")
            conn.rollback()
