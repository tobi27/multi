RÈGLES — MVP SOVEREIGN (Claude Code)

Objectif: prouver qu'un agent IA est économiquement souverain.
Acceptation:
- NET ≥ 0 et GDP/PFLOP > 0 sur N=30 (p95 ≥ 0)
- CRI p50 ≥ 1.30 (CRI = AGDP / ComputeCost)
- P95 latence preuve < 2s (console SUMMARY)

Preuve = 4 piliers réels & auditables:
1) ΔKPI réel (CSV) → $ via contrat (price_per_point) — CONTRACT_HASH loggé
   (à défaut: oracle.json pour entrer ΔKPI% ou $)
2) Compute réel (tokens Anthropic → FLOPs → PFLOPs) + coût ($)
3) Flux $ réel (Stripe test): take-rate / premium — IDs externes stockés
4) Ledger signé (SHA-256 + Ed25519) + SQLite (persist)

Primitives (flags):
SPAWN (seed_cost, α≤0.5) · LEND (r=f(trust)) · INSURE (SLA) · DELEGATE (fee+royalty) · SLASH (bond)

Formules:
AGDP = ΔKPI * price_per_point
PFLOPs = FLOPs / 1e15
ComputeCost = tokens*USD_PER_TOKEN_API + PFLOPs*USD_PER_PFLOP_INFRA
Premium = AGDP * BASE_PREMIUM * (1 - Trust/1000)
Claim = AGDP * COVERAGE  si ΔKPI < SLA
TakeRate = AGDP * TAKE_RATE
NET = AGDP - premium - claim - TakeRate - ComputeCost - royalties - loan_repay
CRI = AGDP / ComputeCost

Sorties obligatoires (SUMMARY):
AGDP, PFLOPs, GDP/PFLOP, ComputeCost, CRI, Premium, Claim, TakeRate, Royalties, LoanRepay, NET, PASSED, RECEIPT, SIG, AnthropicUsageID, StripePI
