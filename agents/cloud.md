SUB-AGENTS
- Producer: génère valeur (CSV+logreg) et/ou LLM; enregistre FLOPs; oracle si présent.
- Insurer: premium/claim selon SLA.
- Monetizer: take-rate + Stripe PaymentIntent (test).
- Accountant: PFLOPs/ComputeCost/CRI/NET; signe ledger; SQLite.
- Spawn/Lend/Delegate: primitives activables par flags; logs.

WORKFLOWS
- run-proof: 1 run (MODE=real si .env), fallback offline si CSV/clé manquants.
- run-parallel: N=30; imprime p50/p95 NET, p50 CRI, p95 GDP/PFLOP.
- run-darwin: Darwinian Engine + mini-MARL (UCB); R rounds, P population; fitness-based token allocation; thermostat control (PRICE↑, COVERAGE↓); exports darwin_results.json.
- cloud-memory-update: nettoyer mémoires <150 lignes cumulées.

DARWIN ENGINE
- Fitness: η = (AGDP/ComputeCost) × trust_multiplier
- Token allocation: softmax over fitness scores, constrained by MIN/MAX per agent
- UCB bandit: exploration/exploitation balance via β parameter
- Thermostat: auto-adjust PRICE_PER_POINT (step up) and COVERAGE (step down) to meet targets
- Targets: CRI p50 ≥ 1.30, NET p95 ≥ 0
- Arm variants: price_mul, coverage_mul variations (±15%)
- R×P runs total, exports statistics + UCB state + thermostat log
