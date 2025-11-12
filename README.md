# Sovereign Agent MVP

**Prouver qu'un agent IA est économiquement souverain.**

Agent autonome qui génère de la valeur mesurable (AGDP), paie ses coûts, et prouve sa rentabilité via 4 piliers auditables.

## 🎯 Objectif

Démontrer la **souveraineté économique** d'un agent IA :
- ✅ NET ≥ 0 (profit positif après tous les coûts)
- ✅ CRI ≥ 1.30 (ratio valeur/coût)
- ✅ GDP/PFLOP > 0 (efficacité compute)
- ✅ Preuve auditable (ledger signé)

## 🏗️ Architecture

### 4 Piliers Réels

1. **ΔKPI → $**
   - CSV réel (`data/events.csv`) OU oracle (`oracle.json`)
   - Logistic regression avec FLOPs comptés
   - Amélioration mesurée vs baseline

2. **Compute → PFLOPs**
   - Anthropic API (tokens réels)
   - FLOPs = 6 × layers × d_model² × tokens
   - Coût = tokens×$0.000008 + PFLOPs×$20

3. **Flux $ → IDs**
   - Stripe PaymentIntent (test mode)
   - Take-rate (15%)
   - Premium assurance
   - IDs externes vérifiables

4. **Ledger → Audit**
   - SHA-256 du payload
   - Ed25519 signature
   - SQLite persistence
   - RECEIPT + SIG + IDs

### Pipeline LangGraph

```
Identity → Spawn → Lend → Producer → Insurer → Monetizer → Delegate → Accountant
```

**Primitives économiques :**
- **SPAWN** : Créer agent enfant (seed cost, α trust)
- **LEND** : Emprunter capital (interest = f(trust))
- **DELEGATE** : Déléguer tâches (fee + royalty)

### Formules

```python
AGDP = ΔKPI × price_per_point + LLM_value
ComputeCost = tokens×USD_PER_TOKEN_API + PFLOPs×USD_PER_PFLOP_INFRA
CRI = AGDP / ComputeCost
Premium = AGDP × BASE_PREMIUM × (1 - Trust/1000)
Claim = AGDP × COVERAGE  si ΔKPI < SLA
TakeRate = AGDP × TAKE_RATE
NET = AGDP - Premium - Claim - TakeRate - ComputeCost - Royalties - LoanRepay
```

## 🚀 Installation

```bash
# 1. Clone
git clone <repo>
cd multi

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure
cp .env.example .env
# Éditer .env avec tes clés API :
#   ANTHROPIC_API_KEY=sk-ant-...
#   STRIPE_SECRET_TEST=sk_test_...

# 4. (Optionnel) Ajouter tes données réelles
# Placer data/events.csv avec colonnes :
#   event_id, timestamp, features_json, label
```

## 📊 Utilisation

### Run unique

```bash
python run_graph.py
```

**Sortie :**
```
AGDP $=750.49 | PFLOPs=2.633e-03 | GDP/PFLOP $=284,994
ComputeCost $=0.06 | CRI=12,508
Premium=$11.29 | Claim=$525.34 | TakeRate=$112.57
NET $=-71.38 | PASSED=False
RECEIPT=8053a39a... | SIG=b0IPp+Fx...
AnthropicUsageID=msg_01PrXg... | StripePI=pi_xxx
```

### Batch parallèle (N=30)

```bash
python run_parallel_batch.py 30
```

**Sortie :**
```
BATCH STATISTICS
NET (Agent Profit):
  Mean:   $45.67
  Median: $52.10
  p95:    $120.50
  StDev:  $38.22

CRI (AGDP/ComputeCost):
  Median: 15,234.50

PASS Rate: 87.0% (26/30)

ACCEPTANCE CRITERIA:
  ✓ NET p95 ≥ 0: $120.50
  ✓ CRI p50 ≥ 1.30: 15,234.50

✓ Results exported to: batch_results.json
```

### Avec oracle (sans CSV)

```bash
# Éditer oracle.json
{
  "delta_kpi_pct": 7.5,
  "tokens_used": 0,
  "override_agdp_usd": null
}

python run_graph.py
```

## 📁 Structure

```
multi/
├── cloud.md                  # Règles & formules
├── requirements.txt          # Dependencies
├── .env.example             # Template config
├── .env                     # Tes clés (gitignored)
├── oracle.json              # ΔKPI externe
├── run_graph.py             # Run unique
├── run_parallel_batch.py    # Batch N runs
├── data/
│   └── events.csv           # Données réelles (100 events)
├── agents/
│   ├── state.py             # GraphState + formules
│   ├── nodes.py             # Pipeline nodes
│   ├── tools.py             # Producer/Insurer/etc tools
│   ├── flops.py             # ML + FLOPs counting
│   ├── llm.py               # Anthropic API
│   ├── payments.py          # Stripe API
│   ├── crypto.py            # Ed25519 signature
│   ├── oracle.py            # Oracle loader
│   └── store.py             # SQLite persistence
└── proofs.sqlite            # Ledger DB (generated)
```

## 🔧 Configuration (.env)

```bash
# API Keys
ANTHROPIC_API_KEY=sk-ant-...
STRIPE_SECRET_TEST=sk_test_...

# Economics
PRICE_PER_POINT=150          # $/point ΔKPI
TAKE_RATE=0.15               # Platform fee (15%)
BASE_PREMIUM=0.08            # Insurance base (8%)
COVERAGE=0.70                # Claim coverage (70%)
USD_PER_TOKEN_API=0.000008   # Anthropic cost
USD_PER_PFLOP_INFRA=20       # Infra cost
TRUST_SCORE=812              # Initial trust (0-1000)
SLA_TARGET=0.05              # Min improvement (5%)

# Primitives
ENABLE_SPAWN=true
ENABLE_LEND=true
ENABLE_DELEGATE=true
SEED_COST_USD=150
LEND_PRINCIPAL_USD=300
DELEGATE_FEE_USD=25

# Security
DISABLE_CRYPTO=false
```

## 🧪 Test avec données synthétiques

Si `data/events.csv` n'existe pas, le système génère automatiquement **5000×50** données synthétiques avec patterns réalistes.

## 📈 Métriques

| Métrique | Description | Critère |
|----------|-------------|---------|
| **AGDP** | Agent GDP ($) | > 0 |
| **NET** | Profit après coûts ($) | ≥ 0 (p95) |
| **CRI** | AGDP/ComputeCost | ≥ 1.30 (p50) |
| **GDP/PFLOP** | $/PFLOP efficiency | > 0 |
| **PASSED** | (NET>0) && (GDP/PFLOP>0) | true |

## 🔐 Sécurité

- **Ed25519** : Signature des ledgers
- **SHA-256** : Hash du payload
- **SQLite** : Persistence audit trail
- **.env** : Gitignored (clés protégées)

## 📤 Exports

### batch_results.json

```json
{
  "statistics": {
    "batch_size": 30,
    "net": {
      "mean": 45.67,
      "median": 52.10,
      "p95": 120.50
    },
    "cri": { "median": 15234.50 },
    "passed_rate": 0.87
  },
  "runs": [
    {
      "run_id": "...",
      "agent_net_usd": 52.10,
      "agdp_usd": 750.49,
      "cri": 12508.17,
      "passed": true,
      "receipt": "8053a39a..."
    }
  ]
}
```

### proofs.sqlite

```sql
SELECT run_id, ts, json->>'$.agent_net_usd' as net
FROM proofs
ORDER BY ts DESC
LIMIT 10;
```

## 🎓 Concepts

### Souveraineté Économique

Un agent est **souverain** s'il :
1. Génère valeur > coûts (NET > 0)
2. Prouve sa valeur (ledger signé)
3. Paie ses dettes (loans, royalties)
4. Respecte SLA (ou paie claims)

### Primitives DeFi-like

- **SPAWN** : Child agents héritent trust×α
- **LEND** : Interest rate inversement proportionnel au trust
- **DELEGATE** : Royalties sur revenus futurs
- **INSURE** : Premium/claim basé sur performance

## 🚨 Troubleshooting

### Stripe 403 Error

```
[STRIPE] Status: 403
[STRIPE] Error response: Access denied
```

**Solution** : Générer nouvelle clé test sur https://dashboard.stripe.com/test/apikeys

### No data/events.csv

**OK** : Le système génère automatiquement 5000 samples synthétiques.

### CRI = None

**Cause** : ComputeCost = 0 (pas de tokens LLM utilisés)

**Solution** : Vérifier `ANTHROPIC_API_KEY` dans `.env`

## 📚 Références

- **LangGraph** : https://langchain-ai.github.io/langgraph/
- **Anthropic API** : https://docs.anthropic.com/
- **Stripe Test** : https://stripe.com/docs/testing

## 🤝 Contributing

Le projet est un **MVP** pour prouver la souveraineté économique des agents IA.

Améliorations bienvenues :
- Nouveaux KPIs métier
- Primitives économiques avancées
- Visualisations des statistiques
- Multi-agent coordination

## 📄 License

MIT
