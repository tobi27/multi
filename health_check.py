#!/usr/bin/env python3
"""
Health check script pour Sovereign Agent MVP
Vérifie: data, APIs, SQLite, crypto keys
"""
import os
import sys
import json
from dotenv import load_dotenv
load_dotenv()

def check_csv_data():
    """Vérifie la présence de data/events.csv"""
    path = "data/events.csv"
    if not os.path.exists(path):
        return False, f"❌ {path} not found"

    with open(path) as f:
        lines = len(f.readlines()) - 1  # -1 for header

    if lines < 10:
        return False, f"❌ {path} has only {lines} events (min 10)"

    return True, f"✅ {path} ({lines} events)"

def check_anthropic_api():
    """Vérifie la clé Anthropic API"""
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        return False, "❌ ANTHROPIC_API_KEY not set"

    if not key.startswith("sk-ant-"):
        return False, f"❌ ANTHROPIC_API_KEY format invalid"

    return True, f"✅ ANTHROPIC_API_KEY configured"

def check_stripe_api():
    """Vérifie la clé Stripe (optionnel)"""
    key = os.getenv("STRIPE_SECRET_TEST")
    if not key:
        return None, "⚠️  STRIPE_SECRET_TEST not set (optional)"

    if not key.startswith("sk_test_"):
        return False, f"❌ STRIPE_SECRET_TEST format invalid"

    return True, f"✅ STRIPE_SECRET_TEST configured"

def check_sqlite():
    """Vérifie SQLite"""
    try:
        import sqlite3
        conn = sqlite3.connect(":memory:")
        conn.close()
        return True, "✅ SQLite available"
    except Exception as e:
        return False, f"❌ SQLite error: {e}"

def check_crypto_key():
    """Vérifie la clé Ed25519"""
    path = ".agent_ed25519.json"
    if not os.path.exists(path):
        return None, f"⚠️  {path} not found (will be auto-generated)"

    try:
        with open(path) as f:
            data = json.load(f)

        # Accept both formats: sk_b64/vk_b64 or private_key/public_key
        has_keys = ("sk_b64" in data and "vk_b64" in data) or \
                   ("private_key" in data and "public_key" in data)

        if not has_keys:
            return False, f"❌ {path} malformed (missing keys)"

        return True, f"✅ {path} valid"
    except Exception as e:
        return False, f"❌ {path} error: {e}"

def check_dependencies():
    """Vérifie les dépendances Python critiques"""
    deps = [
        ("numpy", "numpy"),
        ("anthropic", "anthropic"),
        ("langgraph", "langgraph"),
        ("pynacl", "nacl")  # pynacl installs as 'nacl'
    ]
    results = []

    for display_name, import_name in deps:
        try:
            __import__(import_name)
            results.append((True, f"✅ {display_name}"))
        except ImportError:
            results.append((False, f"❌ {display_name} not installed"))

    all_ok = all(r[0] for r in results)
    return all_ok, "\n    ".join([r[1] for r in results])

def run_health_check():
    """Execute all health checks"""
    print("=" * 60)
    print("SOVEREIGN AGENT MVP - HEALTH CHECK")
    print("=" * 60)

    checks = [
        ("CSV Data", check_csv_data),
        ("Anthropic API", check_anthropic_api),
        ("Stripe API", check_stripe_api),
        ("SQLite", check_sqlite),
        ("Crypto Key", check_crypto_key),
        ("Dependencies", check_dependencies)
    ]

    results = []
    for name, check_fn in checks:
        status, message = check_fn()
        results.append((name, status, message))
        print(f"\n{name}:")
        if isinstance(message, str) and "\n" in message:
            print(f"    {message}")
        else:
            print(f"  {message}")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    critical_failures = sum(1 for _, status, _ in results if status is False)
    warnings = sum(1 for _, status, _ in results if status is None)
    successes = sum(1 for _, status, _ in results if status is True)

    print(f"✅ Passed: {successes}")
    print(f"⚠️  Warnings: {warnings}")
    print(f"❌ Failed: {critical_failures}")

    if critical_failures > 0:
        print("\n❌ SYSTEM NOT READY - Fix critical failures above")
        sys.exit(1)
    elif warnings > 0:
        print("\n⚠️  SYSTEM READY WITH WARNINGS - Some features may be unavailable")
        sys.exit(0)
    else:
        print("\n✅ SYSTEM READY - All checks passed!")
        sys.exit(0)

if __name__ == "__main__":
    run_health_check()
