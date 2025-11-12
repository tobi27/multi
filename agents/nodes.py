"""
LangGraph nodes for Sovereign MVP pipeline.
"""
from .tools import tool_produce_offline, tool_llm_real, tool_online_micro, tool_trust_rating


def producer_node(state):
    """
    Producer agent: generate value via ML/LLM compute.
    Routes to both offline ML and LLM jobs for maximum compute + value.
    """
    # Execute offline ML (real data if available)
    state = tool_produce_offline(state)

    # Execute LLM job (real Anthropic API if key present)
    state = tool_llm_real(
        state,
        prompt="Analyze and clean 50 customer records for quality scoring."
    )

    # Optional: online microtasks
    # state = tool_online_micro(state)

    return state


def insurer_node(state):
    """
    Insurer agent: provide insurance coverage based on trust.
    Computes premium and handles SLA/claims.
    """
    # Trust-based premium calculation
    base_premium = 5.0
    trust_factor = state.trust_score / 1000.0
    premium_eur = base_premium * (1.0 + trust_factor)

    state.premium_eur = premium_eur

    # Define SLA: minimum AGDP threshold
    sla_threshold = 10.0  # minimum €10 AGDP required

    # Check if SLA is met
    if state.agdp_eur < sla_threshold:
        # SLA failed: trigger claim
        claim_amount = premium_eur * 2.0  # 2x premium payout
        state.claim_eur = claim_amount
        state.sla_passed = False
    else:
        state.claim_eur = 0.0
        state.sla_passed = True

    # Update trust based on SLA result
    state = tool_trust_rating(state)

    return state


def platform_node(state):
    """
    Platform node: collect take-rate and compute final accounting.
    """
    # Take-rate: 15% of AGDP
    state.platform_revenue_eur = state.agdp_eur * 0.15

    # Agent net = AGDP - take-rate - premium + claim
    state.agent_net_eur = (
        state.agdp_eur
        - state.platform_revenue_eur
        - state.premium_eur
        + state.claim_eur
    )

    return state


def finalize_node(state):
    """
    Finalize: compute metrics, create ledger, persist to SQLite.
    """
    # Finalize the state (computes GDP/PFLOP, SHA-256, etc.)
    state.finalize()

    return state
