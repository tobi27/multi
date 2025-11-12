"""
LangGraph nodes - MVP Sovereign
Définition des nœuds (agents) du graphe d'orchestration
Pipeline: identity → producer → insurer → monetizer → accountant
"""

import hashlib
import json
import logging
import uuid
from datetime import datetime
from typing import Dict, Any
import numpy as np

from langgraph.graph import StateGraph, END
from .state import AgentState, Ledger, AgentIdentity
from .flops import calculate_logistic_regression_flops, simple_logistic_regression

logger = logging.getLogger(__name__)


def identity_node(state: AgentState) -> AgentState:
    """
    Nœud identity - Identifie et enregistre l'agent sovereign.
    """
    logger.info("🆔 Identity: Création identité agent")

    # Création de l'identité agent
    agent_id = str(uuid.uuid4())
    identity = AgentIdentity(
        agent_id=agent_id,
        agent_name=f"sovereign-{agent_id[:8]}",
        trust_score=750.0,  # Score initial moyen-élevé
        created_at=datetime.now().isoformat()
    )

    # Mise à jour du ledger
    ledger = state["ledger"]
    ledger.identity = identity

    state["current_agent"] = "identity"
    state["messages"].append(f"Identity: Agent {identity.agent_name} créé (Trust={identity.trust_score})")

    logger.info(f"✅ Identity: Agent {identity.agent_name} enregistré")
    return state


def producer_node(state: AgentState) -> AgentState:
    """
    Nœud producer - Production via régression logistique offline avec comptage FLOPs exact.
    """
    logger.info("🏭 Producer: Démarrage production")

    ledger = state["ledger"]
    seed = 42  # Seed fixe pour reproductibilité

    # Paramètres du modèle (simple pour être auditable)
    n_samples = 1000
    n_features = 20
    n_iterations = 50

    # Production: régression logistique simple
    accuracy_before = 0.50  # Baseline (random)
    accuracy_delta, total_flops = simple_logistic_regression(
        n_samples=n_samples,
        n_features=n_features,
        n_iterations=n_iterations,
        seed=seed
    )
    accuracy_after = accuracy_before + (accuracy_delta / 100.0)

    # Mise à jour des métriques de production
    ledger.production.accuracy_delta = accuracy_delta
    ledger.production.flops_used = total_flops
    ledger.production.training_samples = n_samples
    ledger.production.seed = seed

    state["current_agent"] = "producer"
    state["messages"].append(
        f"Producer: Δaccuracy={accuracy_delta:.2f}% "
        f"(baseline {accuracy_before:.2%} → {accuracy_after:.2%}), "
        f"FLOPs={total_flops:,.0f}"
    )

    logger.info(f"✅ Producer: {accuracy_delta:.2f}% accuracy gain, {total_flops:,.0f} FLOPs")
    return state


def insurer_node(state: AgentState) -> AgentState:
    """
    Nœud insurer - Calcul de la prime d'assurance et des claims basés sur SLA.
    """
    logger.info("🛡️  Insurer: Calcul assurance")

    ledger = state["ledger"]

    # Récupération des données
    trust_score = ledger.identity.trust_score if ledger.identity else 500.0
    accuracy_delta = ledger.production.accuracy_delta

    # Paramètres d'assurance
    base_premium = 10.0  # € base
    sla_threshold = 1.0  # Minimum 1% d'amélioration requis

    # Calcul premium: premium = base * (1 - TrustScore/1000)
    # Plus le TrustScore est élevé, moins la prime est chère
    premium = base_premium * (1.0 - trust_score / 1000.0)

    # Calcul claim: si Δacc < SLA, on active le claim
    claim = 0.0
    if accuracy_delta < sla_threshold:
        # Claim = premium * 2 (compensation pour sous-performance)
        claim = premium * 2.0
        logger.warning(f"⚠️  SLA breach: {accuracy_delta:.2f}% < {sla_threshold}% → Claim activé")

    # Mise à jour des métriques d'assurance
    ledger.insurance.premium = premium
    ledger.insurance.claim = claim
    ledger.insurance.sla_threshold = sla_threshold
    ledger.insurance.base_premium = base_premium

    state["current_agent"] = "insurer"
    state["messages"].append(
        f"Insurer: Premium={premium:.2f}€, Claim={claim:.2f}€, SLA={sla_threshold}%"
    )

    logger.info(f"✅ Insurer: Premium={premium:.2f}€, Claim={claim:.2f}€")
    return state


def monetizer_node(state: AgentState) -> AgentState:
    """
    Nœud monetizer - Calcul de l'AGDP et des revenus (plateforme + agent).
    """
    logger.info("💰 Monetizer: Calcul monétisation")

    ledger = state["ledger"]

    # Récupération des données
    accuracy_delta = ledger.production.accuracy_delta
    price_per_point = 10.0  # €/point d'accuracy
    take_rate = 0.15  # 15% pour la plateforme

    # Calcul AGDP: € = price_per_point × Δaccuracy(%)
    agdp = price_per_point * accuracy_delta

    # Calcul revenue plateforme
    platform_revenue = agdp * take_rate

    # Mise à jour des métriques de monétisation
    ledger.monetization.agdp = agdp
    ledger.monetization.take_rate = take_rate
    ledger.monetization.platform_revenue = platform_revenue
    ledger.monetization.price_per_point = price_per_point

    state["current_agent"] = "monetizer"
    state["messages"].append(
        f"Monetizer: AGDP={agdp:.2f}€ (Δacc={accuracy_delta:.2f}% × {price_per_point}€/pt), "
        f"Platform={platform_revenue:.2f}€ ({take_rate*100:.0f}%)"
    )

    logger.info(f"✅ Monetizer: AGDP={agdp:.2f}€, Platform={platform_revenue:.2f}€")
    return state


def accountant_node(state: AgentState) -> AgentState:
    """
    Nœud accountant - Agrégation finale, calcul GDP/PFLOP et génération du receipt SHA-256.
    """
    logger.info("📊 Accountant: Agrégation finale")

    ledger = state["ledger"]

    # Récupération des données
    flops = ledger.production.flops_used
    agdp = ledger.monetization.agdp
    premium = ledger.insurance.premium
    claim = ledger.insurance.claim
    platform_revenue = ledger.monetization.platform_revenue

    # Calculs finaux
    pflops = flops / 1e15  # Conversion en Peta-FLOPs

    # GDP/PFLOP: efficacité économique
    gdp_per_pflop = agdp / pflops if pflops > 0 else 0.0

    # Agent NET: revenu après coûts et commission plateforme
    # NET = AGDP - Platform Revenue - Premium + Claim
    agent_net = agdp - platform_revenue - premium + claim

    # Validation: GDP/PFLOP > 0 ET Agent NET > 0
    passed = bool((gdp_per_pflop > 0) and (agent_net > 0))

    # Mise à jour des métriques comptables
    ledger.accounting.pflops = float(pflops)
    ledger.accounting.gdp_per_pflop = float(gdp_per_pflop)
    ledger.accounting.agent_net = float(agent_net)
    ledger.accounting.passed = passed

    # Génération du receipt (hash SHA-256 du ledger)
    ledger_dict = ledger.to_dict()
    ledger_json = json.dumps(ledger_dict, sort_keys=True)
    receipt_hash = hashlib.sha256(ledger_json.encode()).hexdigest()
    ledger.accounting.receipt = receipt_hash

    state["current_agent"] = "accountant"
    state["messages"].append(
        f"Accountant: GDP/PFLOP={gdp_per_pflop:.2e}€, AgentNET={agent_net:.2f}€, "
        f"PASSED={passed}, RECEIPT={receipt_hash[:16]}..."
    )

    logger.info(f"✅ Accountant: GDP/PFLOP={gdp_per_pflop:.2e}€, NET={agent_net:.2f}€, PASSED={passed}")
    return state


def create_graph() -> StateGraph:
    """
    Crée et configure le graphe LangGraph sovereign.
    Pipeline: identity → producer → insurer → monetizer → accountant

    Returns:
        Graphe compilé prêt à l'exécution
    """
    logger.info("🏗️  Création du graphe LangGraph Sovereign")

    # Création du graphe
    workflow = StateGraph(AgentState)

    # Ajout des nœuds (pipeline sovereign)
    workflow.add_node("identity", identity_node)
    workflow.add_node("producer", producer_node)
    workflow.add_node("insurer", insurer_node)
    workflow.add_node("monetizer", monetizer_node)
    workflow.add_node("accountant", accountant_node)

    # Définition du pipeline linéaire
    workflow.set_entry_point("identity")
    workflow.add_edge("identity", "producer")
    workflow.add_edge("producer", "insurer")
    workflow.add_edge("insurer", "monetizer")
    workflow.add_edge("monetizer", "accountant")
    workflow.add_edge("accountant", END)

    # Compilation
    graph = workflow.compile()
    logger.info("✅ Graphe Sovereign compilé: identity→producer→insurer→monetizer→accountant")

    return graph
