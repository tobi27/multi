# Mémoire Projet - MVP Sovereign

## Règles du projet

Ce projet implémente un système souverain (sovereign) basé sur LangGraph pour l'orchestration d'agents IA.

## Principes

- **Souveraineté**: Le système peut fonctionner en mode offline ou avec LLM
- **Modularité**: Architecture basée sur des agents spécialisés
- **Traçabilité**: Utilisation de la mémoire projet et dossier

## Architecture

- Orchestration via LangGraph (`run_graph.py`)
- Agents modulaires dans `/agents/`
- Configuration via `.env`
- Intégration Claude Code via `commands.json` et `hooks.json`
