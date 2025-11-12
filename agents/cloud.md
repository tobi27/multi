SUB-AGENTS
- Producer: génère valeur (CSV+logreg) et/ou LLM; enregistre FLOPs; oracle si présent.
- Insurer: premium/claim selon SLA.
- Monetizer: take-rate + Stripe PaymentIntent (test).
- Accountant: PFLOPs/ComputeCost/CRI/NET; signe ledger; SQLite.
- Spawn/Lend/Delegate: primitives activables par flags; logs.

WORKFLOWS
- run-proof: 1 run (MODE=real si .env), fallback offline si CSV/clé manquants.
- run-parallel: N=30; imprime p50/p95 NET, p50 CRI, p95 GDP/PFLOP.
- cloud-memory-update: nettoyer mémoires <150 lignes cumulées.
