"""
State management - MVP Sovereign
Définition de l'état partagé entre les agents du graphe
"""

from typing import TypedDict, List, Dict, Any, Optional
from pydantic import BaseModel, Field


class AgentState(TypedDict):
    """
    État global partagé entre tous les agents du graphe.

    Attributes:
        mode: Mode de fonctionnement (offline ou llm)
        messages: Historique des messages échangés
        context: Contexte et métadonnées partagées
        current_agent: Agent actuellement actif
        flops_used: FLOPs consommés jusqu'à présent
        result: Résultat final de l'exécution
    """
    mode: str
    messages: List[str]
    context: Dict[str, Any]
    current_agent: Optional[str]
    flops_used: Optional[float]
    result: Optional[Any]


class Message(BaseModel):
    """Modèle pour un message agent"""
    role: str = Field(description="Rôle de l'émetteur (user, agent, system)")
    content: str = Field(description="Contenu du message")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentConfig(BaseModel):
    """Configuration d'un agent"""
    name: str
    description: str
    tools: List[str] = Field(default_factory=list)
    max_iterations: int = 10
    temperature: float = 0.7
