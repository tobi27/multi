from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import time, uuid, os, json
from .store import save_ledger
from .crypto import sign_ledger, sha256_hex

class ActionRecord(BaseModel):
    kind: str
    details: Dict
    flops: int = 0
    value_usd: float = 0.0

class GraphState(BaseModel):
    ts: int = Field(default_factory=lambda: int(time.time()))
    run_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    trust_score: int = int(os.getenv("TRUST_SCORE", "812"))
    price_per_point: float = float(os.getenv("PRICE_PER_POINT","150"))
    take_rate: float = float(os.getenv("TAKE_RATE","0.15"))
    base_premium_rate: float = float(os.getenv("BASE_PREMIUM","0.08"))
    coverage: float = float(os.getenv("COVERAGE","0.70"))
    improvement_target: float = float(os.getenv("SLA_TARGET","0.05"))
    usd_per_token_api: float = float(os.getenv("USD_PER_TOKEN_API","0.000008"))
    usd_per_pflop_infra: float = float(os.getenv("USD_PER_PFLOP_INFRA","20"))
    contract_hash: str = os.getenv("CONTRACT_HASH","contract_hash_missing")
    vault_usd: float = 0.0
    bond_usd: float = 0.0
    parent_id: Optional[str] = None
    delegators: Dict = Field(default_factory=dict)
    loans: List[Dict] = Field(default_factory=list)
    spawn_params: Dict = Field(default_factory=lambda:{
        "seed_cost_usd": float(os.getenv("SEED_COST_USD","150")),
        "alpha": float(os.getenv("SPAWN_ALPHA","0.4"))
    })
    lend_params: Dict = Field(default_factory=lambda:{
        "principal_usd": float(os.getenv("LEND_PRINCIPAL_USD","300")),
        "base": float(os.getenv("LEND_BASE","0.06")),
        "spread": float(os.getenv("LEND_SPREAD","0.12"))
    })
    delegate_params: Dict = Field(default_factory=lambda:{
        "fee_usd": float(os.getenv("DELEGATE_FEE_USD","25")),
        "royalty": float(os.getenv("DELEGATE_ROYALTY","0.08")),
        "delegate_id": "agent-deleg-1"
    })
    actions: List[ActionRecord] = Field(default_factory=list)
    total_flops: int = 0
    tokens_used: int = 0
    agdp_usd: float = 0.0
    compute_cost_usd: float = 0.0
    platform_revenue_usd: float = 0.0
    premium_usd: float = 0.0
    claim_usd: float = 0.0
    royalties_usd: float = 0.0
    loans_repaid_usd: float = 0.0
    agent_net_usd: float = 0.0
    gdp_per_pflop_usd: Optional[float] = None
    cri: Optional[float] = None
    baseline_acc: Optional[float] = None
    acc: Optional[float] = None
    improvement: Optional[float] = None
    anthropic_usage_id: Optional[str] = None
    stripe_payment_intent_id: Optional[str] = None
    receipt: Optional[str] = None
    signature_b64: Optional[str] = None
    verify_key_b64: Optional[str] = None
    passed: Optional[bool] = None

    def finalize(self):
        pf = self.total_flops / 1e15
        self.gdp_per_pflop_usd = None if pf==0 else round(self.agdp_usd / pf, 2)
        self.compute_cost_usd = round(self.tokens_used*self.usd_per_token_api + pf*self.usd_per_pflop_infra, 2)
        self.cri = None if self.compute_cost_usd<=0 else round(self.agdp_usd / self.compute_cost_usd, 2)
        self.platform_revenue_usd = round(self.agdp_usd * self.take_rate, 2)
        premium_rate = self.base_premium_rate * (1 - self.trust_score/1000)
        self.premium_usd = round(self.agdp_usd * premium_rate, 2)
        self.claim_usd = 0.0
        if (self.improvement or 0) < self.improvement_target:
            self.claim_usd = round(self.agdp_usd * self.coverage, 2)
        self.royalties_usd = 0.0
        for d in self.delegators.values(): self.royalties_usd += self.agdp_usd * d["royalty"]
        self.royalties_usd = round(self.royalties_usd, 2)
        repay_total = 0.0
        for ln in self.loans:
            pay = min(ln["due"], max(0.0, self.agdp_usd*0.15))
            ln["due"] = round(ln["due"] - pay, 2)
            repay_total += pay
        self.loans_repaid_usd = round(repay_total, 2)
        self.agent_net_usd = round(
            self.agdp_usd - self.premium_usd - self.claim_usd - self.platform_revenue_usd
            - self.compute_cost_usd - self.royalties_usd - self.loans_repaid_usd,
            2
        )
        self.passed = bool((self.agent_net_usd > 0) and (self.gdp_per_pflop_usd or 0) > 0)
        payload = self.model_dump()
        self.receipt = sha256_hex(payload)
        sig, vk = sign_ledger(payload)
        self.signature_b64, self.verify_key_b64 = sig, vk
        save_ledger(self.run_id, payload)
        return self
