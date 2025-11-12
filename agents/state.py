"""
Graph state definition for Sovereign MVP.
"""
import time
import hashlib
import json
from typing import List
from pydantic import BaseModel, Field


class ActionRecord(BaseModel):
    """Single action record."""
    kind: str
    details: dict = Field(default_factory=dict)
    flops: int = 0
    value_eur: float = 0.0


class GraphState(BaseModel):
    """Main state for the Sovereign agent pipeline."""

    # Identity
    run_id: str = ""
    agent_id: str = "agent_001"

    # Economics
    agdp_eur: float = 0.0
    premium_eur: float = 0.0
    claim_eur: float = 0.0
    platform_revenue_eur: float = 0.0
    agent_net_eur: float = 0.0

    # Compute
    total_flops: int = 0
    total_pflops: float = 0.0

    # Metrics
    gdp_per_pflop_eur: float = 0.0
    sla_passed: bool = False

    # Trust
    trust_score: int = 500  # 0-1000

    # Parameters
    price_per_point: float = 150.0  # € per percentage point improvement

    # Actions log
    actions: List[ActionRecord] = Field(default_factory=list)

    # Ledger
    timestamp: float = 0.0
    sha256: str = ""

    # External proofs
    stripe_intents: List[dict] = Field(default_factory=list)

    def finalize(self):
        """
        Finalize the state:
        - Compute total PFLOPs
        - Compute GDP/PFLOP
        - Generate SHA-256 ledger hash
        - Call Stripe API (test mode) for take-rate and premium
        - Persist to SQLite
        """
        from .payments import stripe_capture_safe
        from .store import save_ledger

        # Compute PFLOPs
        self.total_pflops = self.total_flops / 1e15

        # Compute GDP per PFLOP
        if self.total_pflops > 0:
            self.gdp_per_pflop_eur = self.agdp_eur / self.total_pflops
        else:
            self.gdp_per_pflop_eur = 0.0

        # Timestamp
        self.timestamp = time.time()

        # SHA-256 ledger
        ledger_data = {
            "run_id": self.run_id,
            "agent_id": self.agent_id,
            "agdp_eur": self.agdp_eur,
            "total_pflops": self.total_pflops,
            "premium_eur": self.premium_eur,
            "claim_eur": self.claim_eur,
            "platform_revenue_eur": self.platform_revenue_eur,
            "agent_net_eur": self.agent_net_eur,
            "sla_passed": self.sla_passed,
            "timestamp": self.timestamp,
            "actions": [a.model_dump() for a in self.actions]
        }
        ledger_json = json.dumps(ledger_data, sort_keys=True)
        self.sha256 = hashlib.sha256(ledger_json.encode()).hexdigest()

        # Stripe capture (test mode)
        # 1. Platform take-rate
        if self.platform_revenue_eur > 0.01:
            success, result = stripe_capture_safe(
                self.platform_revenue_eur,
                f"Platform take-rate | run={self.run_id}"
            )
            if success:
                self.stripe_intents.append({
                    "type": "take_rate",
                    "intent_id": result.get("intent_id"),
                    "amount_eur": result.get("amount_eur")
                })

        # 2. Insurance premium
        if self.premium_eur > 0.01:
            success, result = stripe_capture_safe(
                self.premium_eur,
                f"Insurance premium | run={self.run_id}"
            )
            if success:
                self.stripe_intents.append({
                    "type": "premium",
                    "intent_id": result.get("intent_id"),
                    "amount_eur": result.get("amount_eur")
                })

        # Persist to SQLite
        payload = self.model_dump()
        try:
            save_ledger(self.run_id, payload)
        except Exception as e:
            print(f"[WARN] Could not save ledger to SQLite: {e}")

    def summary(self):
        """Generate a summary dict for display."""
        return {
            "RUN_ID": self.run_id,
            "AGENT_ID": self.agent_id,
            "AGDP_EUR": f"{self.agdp_eur:.2f}",
            "TOTAL_PFLOPS": f"{self.total_pflops:.6f}",
            "GDP_PER_PFLOP": f"{self.gdp_per_pflop_eur:.2f}",
            "PREMIUM_EUR": f"{self.premium_eur:.2f}",
            "CLAIM_EUR": f"{self.claim_eur:.2f}",
            "PLATFORM_REVENUE_EUR": f"{self.platform_revenue_eur:.2f}",
            "AGENT_NET_EUR": f"{self.agent_net_eur:.2f}",
            "SLA_PASSED": self.sla_passed,
            "TRUST_SCORE": self.trust_score,
            "SHA256": self.sha256[:16] + "...",
            "STRIPE_INTENTS": len(self.stripe_intents),
            "N_ACTIONS": len(self.actions)
        }
