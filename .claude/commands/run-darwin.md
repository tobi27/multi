---
description: Run Darwinian Engine with UCB-based adaptive token allocation
---

Execute the Darwinian Engine + mini-MARL (UCB) pipeline with:
- R rounds of evolution with P population per round
- Fitness-based token allocation via softmax
- Upper Confidence Bound (UCB) for arm selection
- Thermostat control to adjust PRICE_PER_POINT and COVERAGE
- Target: CRI p50 ≥ 1.30, NET p95 ≥ 0

Run with:
```bash
python run_darwin.py
```

Configuration (via .env):
- DE_ROUNDS: Number of evolution rounds (default: 3)
- DE_POP: Population size per round (default: 4)
- DE_BUDGET_TOKENS: Total token budget per round (default: 120000)
- DE_MIN_TOKENS_AGENT: Minimum tokens per agent (default: 4000)
- DE_MAX_TOKENS_AGENT: Maximum tokens per agent (default: 60000)
- DE_TARGET_CRI: Target CRI threshold (default: 1.30)
- DE_TARGET_P95_NET: Target NET p95 threshold (default: 0.0)
- UCB_BETA: Exploration coefficient (default: 0.5)
- VARIATION_RATE: Arm variation rate (default: 0.15)

Results exported to: darwin_results.json
