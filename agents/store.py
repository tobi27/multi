import sqlite3, json, time
DB="proofs.sqlite"

def save_ledger(run_id: str, payload: dict):
    conn=sqlite3.connect(DB); c=conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS proofs(run_id TEXT PRIMARY KEY, ts INTEGER, json TEXT)")
    c.execute("INSERT OR REPLACE INTO proofs VALUES(?,?,?)", (run_id, int(time.time()), json.dumps(payload)))
    conn.commit(); conn.close()
