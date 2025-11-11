"""
LangGraph nodes - MVP Sovereign
Définition des nœuds (agents) du graphe d'orchestration
"""

from typing import Dict, Any
from langgraph.graph import StateGraph, END
from .state import AgentState
from .tools import execute_tool, get_available_tools
from .flops import calculate_flops, estimate_cost
import logging

logger = logging.getLogger(__name__)


def router_node(state: AgentState) -> AgentState:
    """
    Nœud routeur - Détermine le prochain agent à exécuter.
    """
    logger.info("🔀 Routeur: Analyse de l'état")

    mode = state.get("mode", "offline")
    messages = state.get("messages", [])

    # Logique de routage simple
    if len(messages) == 0:
        next_agent = "analyzer"
    elif len(messages) < 3:
        next_agent = "processor"
    else:
        next_agent = "finalizer"

    state["current_agent"] = next_agent
    state["messages"].append(f"Routeur: Redirection vers {next_agent}")

    return state


def analyzer_node(state: AgentState) -> AgentState:
    """
    Nœud analyseur - Analyse l'entrée et le contexte.
    """
    logger.info("🔍 Analyzer: Démarrage analyse")

    mode = state.get("mode", "offline")
    flops = calculate_flops("simple", {"complexity": 1.0})

    state["messages"].append("Analyzer: Analyse effectuée")
    state["flops_used"] = state.get("flops_used", 0) + flops
    state["context"]["analyzed"] = True

    # Utilise un outil
    timestamp = execute_tool("timestamp", mode)
    state["context"]["analysis_time"] = timestamp

    return state


def processor_node(state: AgentState) -> AgentState:
    """
    Nœud processeur - Effectue le traitement principal.
    """
    logger.info("⚙️  Processor: Traitement en cours")

    mode = state.get("mode", "offline")
    complexity = 2.0 if mode == "llm" else 1.0
    flops = calculate_flops("llm_call" if mode == "llm" else "simple", {"complexity": complexity})

    state["messages"].append(f"Processor: Traitement en mode {mode}")
    state["flops_used"] = state.get("flops_used", 0) + flops
    state["context"]["processed"] = True

    return state


def finalizer_node(state: AgentState) -> AgentState:
    """
    Nœud finaliseur - Finalise et retourne le résultat.
    """
    logger.info("✅ Finalizer: Finalisation")

    mode = state.get("mode", "offline")
    total_flops = state.get("flops_used", 0)
    cost_estimate = estimate_cost(total_flops, mode)

    state["messages"].append("Finalizer: Exécution terminée")
    state["result"] = {
        "status": "success",
        "mode": mode,
        "total_flops": total_flops,
        "cost": cost_estimate,
        "messages_count": len(state["messages"]),
    }

    return state


def should_continue(state: AgentState) -> str:
    """
    Fonction de décision - Détermine si on continue ou termine.
    """
    current = state.get("current_agent")
    messages_count = len(state.get("messages", []))

    if messages_count >= 6 or state.get("result"):
        return "end"

    if current == "analyzer":
        return "processor"
    elif current == "processor":
        return "finalizer"
    else:
        return "end"


def create_graph() -> StateGraph:
    """
    Crée et configure le graphe LangGraph.

    Returns:
        Graphe compilé prêt à l'exécution
    """
    logger.info("🏗️  Création du graphe LangGraph")

    # Création du graphe
    workflow = StateGraph(AgentState)

    # Ajout des nœuds
    workflow.add_node("router", router_node)
    workflow.add_node("analyzer", analyzer_node)
    workflow.add_node("processor", processor_node)
    workflow.add_node("finalizer", finalizer_node)

    # Définition du point d'entrée
    workflow.set_entry_point("router")

    # Ajout des arêtes conditionnelles
    workflow.add_conditional_edges(
        "router",
        should_continue,
        {
            "analyzer": "analyzer",
            "processor": "processor",
            "finalizer": "finalizer",
            "end": END,
        }
    )

    workflow.add_conditional_edges(
        "analyzer",
        should_continue,
        {
            "processor": "processor",
            "end": END,
        }
    )

    workflow.add_conditional_edges(
        "processor",
        should_continue,
        {
            "finalizer": "finalizer",
            "end": END,
        }
    )

    workflow.add_edge("finalizer", END)

    # Compilation
    graph = workflow.compile()
    logger.info("✅ Graphe compilé avec succès")

    return graph
