---
description: Run Sovereign MVP with REAL data (CSV + Anthropic LLM + Stripe test)
---

Execute the Sovereign MVP pipeline with:
- Real data from data/events.csv
- Live Anthropic API calls (if ANTHROPIC_API_KEY set)
- Stripe test mode payment intents (if STRIPE_SECRET_TEST set)
- SQLite persistence for audit trail

Run with environment variables:
```bash
python run_graph.py
```

Required env vars for full real mode:
- ANTHROPIC_API_KEY: Your Anthropic API key
- STRIPE_SECRET_TEST: Your Stripe test secret key

If these are not set, the system will fallback gracefully to synthetic mode.
