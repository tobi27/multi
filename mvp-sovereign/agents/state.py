"""
State management - MVP Sovereign
Définition de l'état partagé entre les agents du graphe
"""

from typing import TypedDict, List, Dict, Any, Optional
from pydantic import BaseModel, Field


class AgentIdentity(BaseModel):
    """Identité d'un agent sovereign"""
    agent_id: str = Field(description="Identifiant unique de l'agent")
    agent_name: str = Field(description="Nom de l'agent")
    trust_score: float = Field(default=500.0, description="Score de confiance 0-1000")
    created_at: str = Field(description="Timestamp de création")


class ProductionMetrics(BaseModel):
    """Métriques de production d'un agent"""
    accuracy_delta: float = Field(default=0.0, description="Amélioration accuracy (%)")
    flops_used: float = Field(default=0.0, description="FLOPs consommés")
    training_samples: int = Field(default=0, description="Nombre d'échantillons")
    seed: int = Field(default=42, description="Seed pour reproductibilité")


class InsuranceMetrics(BaseModel):
    """Métriques d'assurance"""
    premium: float = Field(default=0.0, description="Prime d'assurance (€)")
    claim: float = Field(default=0.0, description="Réclamation (€)")
    sla_threshold: float = Field(default=1.0, description="Seuil SLA accuracy (%)")
    base_premium: float = Field(default=10.0, description="Prime de base (€)")


class MonetizationMetrics(BaseModel):
    """Métriques de monétisation"""
    agdp: float = Field(default=0.0, description="Agent Gross Domestic Product (€)")
    take_rate: float = Field(default=0.15, description="Taux de commission plateforme")
    platform_revenue: float = Field(default=0.0, description="Revenu plateforme (€)")
    price_per_point: float = Field(default=10.0, description="Prix par point d'accuracy (€)")


class AccountingMetrics(BaseModel):
    """Métriques comptables finales"""
    pflops: float = Field(default=0.0, description="Peta-FLOPs (FLOPs / 10^15)")
    gdp_per_pflop: float = Field(default=0.0, description="GDP/PFLOP (€)")
    agent_net: float = Field(default=0.0, description="Revenu net agent (€)")
    passed: bool = Field(default=False, description="Validation GDP/PFLOP > 0 et NET > 0")
    receipt: str = Field(default="", description="Hash SHA-256 du ledger")


class Ledger(BaseModel):
    """Ledger complet de l'exécution"""
    identity: Optional[AgentIdentity] = None
    production: ProductionMetrics = Field(default_factory=ProductionMetrics)
    insurance: InsuranceMetrics = Field(default_factory=InsuranceMetrics)
    monetization: MonetizationMetrics = Field(default_factory=MonetizationMetrics)
    accounting: AccountingMetrics = Field(default_factory=AccountingMetrics)

    def to_dict(self) -> Dict[str, Any]:
        """Convertit le ledger en dictionnaire pour hashing"""
        return {
            "identity": self.identity.model_dump() if self.identity else {},
            "production": self.production.model_dump(),
            "insurance": self.insurance.model_dump(),
            "monetization": self.monetization.model_dump(),
            "accounting": self.accounting.model_dump(),
        }


class AgentState(TypedDict):
    """
    État global partagé entre tous les agents du graphe.

    Attributes:
        mode: Mode de fonctionnement (offline ou llm)
        messages: Historique des messages échangés
        current_agent: Agent actuellement actif
        ledger: Ledger contenant toutes les métriques
        context: Contexte et métadonnées additionnelles
    """
    mode: str
    messages: List[str]
    current_agent: Optional[str]
    ledger: Ledger
    context: Dict[str, Any]


class AgentConfig(BaseModel):
    """Configuration d'un agent"""
    name: str
    description: str
    tools: List[str] = Field(default_factory=list)
    max_iterations: int = 10
    temperature: float = 0.7
