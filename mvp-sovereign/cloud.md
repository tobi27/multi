# Mémoire Projet - MVP Sovereign

## OBJECTIF DU PROJET

Démontrer en live que des agents IA, identifiés et assurés, génèrent un **AGDP net positif** et un **GDP/PFLOP > 0**.

**Preuve** = exécution instrumentée + ledger signé (SHA-256) + métriques financières.

### Contexte
Audience: CEO/Deputy intéressés par "**algorithmic sovereignty**" = valeur nette par unité de compute.

On mesure les **FLOPs réels** (matmuls), on convertit la production en € via Δaccuracy (%), on applique assurance (prime/claim) + monétisation (take-rate).

## RÈGLES MVP SOVEREIGN (Claude Code)

### Objectif Technique
Démontrer **"GDP/PFLOP > 0"** + **"Agent NET > 0"** avec ledger SHA-256.

### Graphe d'Agents (LangGraph)
```
identity → producer → insurer → monetizer → accountant
```

### Production
- **Méthode**: Régression logistique offline avec FLOPs exacts (matmuls)
- **Mode**: Calculs matriciels traçables (pas d'approximations)
- **Seed**: Fixe pour reproductibilité

### Modèle de Valeur
```
€ = price_per_point × Δaccuracy(%)
```

### Système d'Assurance
- **Premium**: `premium = base × (1 - TrustScore/1000)`
- **Claim**: Déclenchement si `Δacc < SLA`
- **TrustScore**: Métrique de confiance 0-1000

### Monétisation
- **Take Rate**: Pourcentage de la plateforme sur les revenus agents
- **Revenue**: Calculé par l'agent monetizer

### Sorties Obligatoires
Chaque exécution DOIT produire:
- `AGDP` (€) - Agent Gross Domestic Product
- `FLOPs` - Opérations virgule flottante totales
- `PFLOPs` - Peta-FLOPs (FLOPs / 10^15)
- `GDP/PFLOP` (€) - Efficacité économique
- `Premium` (€) - Prime d'assurance
- `Claim` (€) - Réclamation d'assurance
- `PlatformRevenue` (€) - Revenu plateforme
- `AgentNET` (€) - Revenu net agent
- `PASSED` (bool) - Validation des critères
- `RECEIPT` (SHA-256) - Hash du ledger

### Contraintes Techniques
- 🔒 **Déterministe**: Seed fixe pour reproductibilité
- 🔒 **Pas d'appels réseau**: Hors démo (mode offline)
- 🔒 **Code court**: Auditable, sans yolo mode
- 🔒 **FLOPs exacts**: Comptage précis des matmuls

### Interdictions
- ❌ Packages lourds (TensorFlow, PyTorch, etc.)
- ❌ Network calls non nécessaires
- ❌ Code "YOLO" sans hooks de validation
- ❌ Approximations non documentées

### Style de Développement
- ✅ **Exécutable**: Code fonctionnel à chaque commit
- ✅ **Mesurable**: Toutes les métriques loggées
- ✅ **Reproductible**: Seed fixe, résultats déterministes
- ✅ **Auditable**: Code court et transparent

## Architecture Technique

- **Orchestration**: LangGraph (`run_graph.py`)
- **Agents**: Modulaires dans `/agents/`
- **Configuration**: `.env` (MODE=offline par défaut)
- **Intégration**: Claude Code via `commands.json` et `hooks.json`
- **Ledger**: SHA-256 pour traçabilité

## Principes

- **Souveraineté**: Fonctionne offline (pas de dépendance cloud)
- **Transparence**: Chaque FLOP tracé et compté
- **Économie**: GDP/PFLOP mesure l'efficacité agent
