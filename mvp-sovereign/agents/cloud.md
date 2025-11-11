# Mémoire Dossier - Agents

## Noisette d'IA-native

Ce dossier contient les composants agents du système sovereign:

- **state.py**: Définition de l'état partagé entre agents
- **flops.py**: Calculs et métriques FLOPs pour l'optimisation
- **tools.py**: Outils et fonctions utilisables par les agents
- **nodes.py**: Nœuds du graphe LangGraph (agents individuels)

## Architecture Agents

Chaque agent est un nœud dans le graphe LangGraph qui:
1. Reçoit l'état courant
2. Effectue son traitement
3. Retourne l'état mis à jour

## Mode Offline vs LLM

- **Offline**: Agents basés sur des règles et heuristiques
- **LLM**: Agents avec capacités de raisonnement via LLM
