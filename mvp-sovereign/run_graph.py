#!/usr/bin/env python3
"""
Orchestration LangGraph - MVP Sovereign
Point d'entrée principal pour l'exécution du graphe d'agents
"""

import os
from dotenv import load_dotenv
from agents.state import AgentState
from agents.nodes import create_graph

def main():
    """Lance l'orchestration du graphe d'agents"""
    load_dotenv()

    mode = os.getenv("MODE", "offline")
    print(f"🚀 Démarrage MVP Sovereign en mode: {mode}")

    # Création du graphe
    graph = create_graph()

    # État initial
    initial_state = AgentState(
        mode=mode,
        messages=[],
        context={}
    )

    # Exécution
    result = graph.invoke(initial_state)
    print(f"✅ Exécution terminée: {result}")

if __name__ == "__main__":
    main()
