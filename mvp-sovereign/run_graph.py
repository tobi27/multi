#!/usr/bin/env python3
"""
Orchestration LangGraph - MVP Sovereign
Point d'entrée principal pour l'exécution du graphe d'agents
Pipeline: identity → producer → insurer → monetizer → accountant
"""

import os
import sys
import logging
from dotenv import load_dotenv

from agents.state import AgentState, Ledger
from agents.nodes import create_graph

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def display_kpis(ledger: Ledger) -> None:
    """
    Affiche tous les KPIs obligatoires du MVP Sovereign.
    """
    print("\n" + "=" * 80)
    print("📊 MVP SOVEREIGN - RÉSULTATS FINAUX")
    print("=" * 80)

    # Identity
    if ledger.identity:
        print(f"\n🆔 IDENTITY")
        print(f"   Agent: {ledger.identity.agent_name}")
        print(f"   ID: {ledger.identity.agent_id}")
        print(f"   Trust Score: {ledger.identity.trust_score}/1000")

    # Production
    print(f"\n🏭 PRODUCTION")
    print(f"   Accuracy Δ: {ledger.production.accuracy_delta:.2f}%")
    print(f"   FLOPs: {ledger.production.flops_used:,.0f}")
    print(f"   Training Samples: {ledger.production.training_samples:,}")
    print(f"   Seed: {ledger.production.seed}")

    # Insurance
    print(f"\n🛡️  INSURANCE")
    print(f"   Premium: {ledger.insurance.premium:.2f}€")
    print(f"   Claim: {ledger.insurance.claim:.2f}€")
    print(f"   SLA Threshold: {ledger.insurance.sla_threshold:.1f}%")
    sla_status = "✅ MET" if ledger.production.accuracy_delta >= ledger.insurance.sla_threshold else "❌ BREACH"
    print(f"   SLA Status: {sla_status}")

    # Monetization
    print(f"\n💰 MONETIZATION")
    print(f"   AGDP: {ledger.monetization.agdp:.2f}€")
    print(f"   Price per Point: {ledger.monetization.price_per_point:.2f}€")
    print(f"   Take Rate: {ledger.monetization.take_rate*100:.1f}%")
    print(f"   Platform Revenue: {ledger.monetization.platform_revenue:.2f}€")

    # Accounting
    print(f"\n📊 ACCOUNTING")
    print(f"   FLOPs: {ledger.production.flops_used:,.0f}")
    print(f"   PFLOPs: {ledger.accounting.pflops:.6e}")
    print(f"   GDP/PFLOP: {ledger.accounting.gdp_per_pflop:.2e}€")
    print(f"   Agent NET: {ledger.accounting.agent_net:.2f}€")

    # Validation
    print(f"\n✅ VALIDATION")
    passed_symbol = "✅ PASSED" if ledger.accounting.passed else "❌ FAILED"
    print(f"   Status: {passed_symbol}")
    print(f"   GDP/PFLOP > 0: {'✅' if ledger.accounting.gdp_per_pflop > 0 else '❌'} ({ledger.accounting.gdp_per_pflop:.2e}€)")
    print(f"   Agent NET > 0: {'✅' if ledger.accounting.agent_net > 0 else '❌'} ({ledger.accounting.agent_net:.2f}€)")

    # Receipt
    print(f"\n🧾 RECEIPT (SHA-256)")
    print(f"   {ledger.accounting.receipt}")

    print("\n" + "=" * 80)


def display_summary_table(ledger: Ledger) -> None:
    """
    Affiche un tableau récapitulatif des KPIs obligatoires.
    """
    print("\n📋 SUMMARY - KPIs OBLIGATOIRES")
    print("-" * 80)
    print(f"{'Metric':<25} {'Value':<30} {'Unit':<10}")
    print("-" * 80)
    print(f"{'AGDP':<25} {ledger.monetization.agdp:>29.2f} {'€':<10}")
    print(f"{'FLOPs':<25} {ledger.production.flops_used:>29,.0f} {'':<10}")
    print(f"{'PFLOPs':<25} {ledger.accounting.pflops:>29.6e} {'':<10}")
    print(f"{'GDP/PFLOP':<25} {ledger.accounting.gdp_per_pflop:>29.2e} {'€':<10}")
    print(f"{'Premium':<25} {ledger.insurance.premium:>29.2f} {'€':<10}")
    print(f"{'Claim':<25} {ledger.insurance.claim:>29.2f} {'€':<10}")
    print(f"{'Platform Revenue':<25} {ledger.monetization.platform_revenue:>29.2f} {'€':<10}")
    print(f"{'Agent NET':<25} {ledger.accounting.agent_net:>29.2f} {'€':<10}")
    passed_str = "PASSED" if ledger.accounting.passed else "FAILED"
    print(f"{'PASSED':<25} {passed_str:>30} {'':<10}")
    print(f"{'RECEIPT':<25} {ledger.accounting.receipt[:30]:>30} {'...':<10}")
    print("-" * 80)


def main():
    """Lance l'orchestration du graphe d'agents sovereign"""
    load_dotenv()

    mode = os.getenv("MODE", "offline")

    print("\n" + "=" * 80)
    print("🚀 MVP SOVEREIGN - DÉMARRAGE")
    print("=" * 80)
    print(f"Mode: {mode}")
    print(f"Pipeline: identity → producer → insurer → monetizer → accountant")
    print("=" * 80 + "\n")

    # Création du graphe
    logger.info("🏗️  Création du graphe LangGraph")
    graph = create_graph()

    # État initial avec ledger
    initial_state: AgentState = {
        "mode": mode,
        "messages": [],
        "current_agent": None,
        "ledger": Ledger(),
        "context": {}
    }

    logger.info("▶️  Lancement de l'exécution")
    print("\n🔄 EXÉCUTION DU PIPELINE\n")

    try:
        # Exécution du graphe
        result = graph.invoke(initial_state)

        # Affichage des messages d'exécution
        print("\n📝 TRACE D'EXÉCUTION:")
        print("-" * 80)
        for msg in result["messages"]:
            print(f"  • {msg}")
        print("-" * 80)

        # Affichage des KPIs
        ledger = result["ledger"]
        display_kpis(ledger)
        display_summary_table(ledger)

        # Statut de sortie
        if ledger.accounting.passed:
            print("\n✅ SUCCESS: MVP Sovereign validation passed!")
            print(f"   • GDP/PFLOP = {ledger.accounting.gdp_per_pflop:.2e}€ > 0 ✅")
            print(f"   • Agent NET = {ledger.accounting.agent_net:.2f}€ > 0 ✅")
            sys.exit(0)
        else:
            print("\n❌ FAILURE: MVP Sovereign validation failed!")
            if ledger.accounting.gdp_per_pflop <= 0:
                print(f"   • GDP/PFLOP = {ledger.accounting.gdp_per_pflop:.2e}€ ≤ 0 ❌")
            if ledger.accounting.agent_net <= 0:
                print(f"   • Agent NET = {ledger.accounting.agent_net:.2f}€ ≤ 0 ❌")
            sys.exit(1)

    except Exception as e:
        logger.error(f"❌ Erreur lors de l'exécution: {e}", exc_info=True)
        print(f"\n❌ ERREUR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
