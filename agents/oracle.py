import json, os
ORACLE_FILE = os.getenv("ORACLE_FILE", "oracle.json")

def load_oracle():
    if not os.path.exists(ORACLE_FILE):
        return None
    with open(ORACLE_FILE, "r") as f:
        try:
            data = json.load(f)
        except Exception:
            return None
    return {
        "delta_kpi_pct": float(data.get("delta_kpi_pct", 0.0)),
        "tokens_used": int(data.get("tokens_used", 0)),
        "override_agdp_eur": data.get("override_agdp_eur", None),
    }
