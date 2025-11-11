"""
Tools and utilities - MVP Sovereign
Outils et fonctions utilisables par les agents
"""

from typing import List, Dict, Any, Callable
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def get_available_tools(mode: str = "offline") -> List[Dict[str, Any]]:
    """
    Retourne la liste des outils disponibles selon le mode.

    Args:
        mode: Mode de fonctionnement (offline ou llm)

    Returns:
        Liste des outils disponibles
    """
    base_tools = [
        {
            "name": "logger",
            "description": "Enregistre des messages dans les logs",
            "function": log_message,
        },
        {
            "name": "timestamp",
            "description": "Retourne le timestamp actuel",
            "function": get_timestamp,
        },
        {
            "name": "context_manager",
            "description": "Gère le contexte partagé",
            "function": manage_context,
        },
    ]

    if mode == "llm":
        base_tools.extend([
            {
                "name": "llm_query",
                "description": "Effectue une requête LLM",
                "function": llm_query,
            },
        ])

    logger.info(f"Outils disponibles en mode {mode}: {len(base_tools)}")
    return base_tools


def log_message(message: str, level: str = "INFO") -> Dict[str, Any]:
    """Enregistre un message dans les logs"""
    logger.log(getattr(logging, level, logging.INFO), message)
    return {
        "status": "logged",
        "message": message,
        "timestamp": datetime.now().isoformat(),
    }


def get_timestamp() -> str:
    """Retourne le timestamp actuel ISO 8601"""
    return datetime.now().isoformat()


def manage_context(action: str, key: str = None, value: Any = None) -> Dict[str, Any]:
    """
    Gère le contexte partagé entre agents.

    Args:
        action: Action à effectuer (get, set, delete, list)
        key: Clé du contexte
        value: Valeur à définir (pour set)

    Returns:
        Résultat de l'opération
    """
    # Note: Dans une vraie implémentation, ceci utiliserait l'état LangGraph
    if action == "get":
        return {"action": "get", "key": key, "value": None}
    elif action == "set":
        return {"action": "set", "key": key, "value": value, "status": "success"}
    elif action == "list":
        return {"action": "list", "keys": []}

    return {"error": "Action non reconnue"}


def llm_query(prompt: str, model: str = "claude-3-sonnet") -> Dict[str, Any]:
    """
    Effectue une requête LLM (placeholder en mode offline).

    Args:
        prompt: Prompt à envoyer au LLM
        model: Modèle à utiliser

    Returns:
        Réponse du LLM
    """
    logger.warning("llm_query appelé - nécessite mode LLM actif")
    return {
        "status": "offline",
        "message": "LLM non disponible en mode offline",
        "prompt": prompt,
        "model": model,
    }


def execute_tool(tool_name: str, mode: str, **kwargs) -> Any:
    """
    Exécute un outil par son nom.

    Args:
        tool_name: Nom de l'outil
        mode: Mode de fonctionnement
        **kwargs: Arguments pour l'outil

    Returns:
        Résultat de l'exécution
    """
    tools = {tool["name"]: tool["function"] for tool in get_available_tools(mode)}

    if tool_name not in tools:
        logger.error(f"Outil inconnu: {tool_name}")
        return {"error": f"Outil {tool_name} non trouvé"}

    try:
        return tools[tool_name](**kwargs)
    except Exception as e:
        logger.error(f"Erreur exécution {tool_name}: {e}")
        return {"error": str(e)}
