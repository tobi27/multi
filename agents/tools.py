"""
Agent tools for Producer and Insurer nodes.
"""
from .flops import train_logreg_count_flops_real, train_logreg_count_flops
from .llm import llm_job
from .state import ActionRecord


def tool_produce_offline(state):
    """
    Offline ML training: logistic regression with real or synthetic data.
    Measures Δaccuracy and FLOPs.
    """
    # Try real data first
    r = train_logreg_count_flops_real(price_per_point=state.price_per_point)

    if r is None:
        # Fallback to synthetic
        r = train_logreg_count_flops(
            n=200,
            d=4,
            price_per_point=state.price_per_point,
            seed=42
        )
        value_eur = state.price_per_point * (r["improvement"] * 100.0)
    else:
        # Real data: value already computed
        value_eur = r["value_eur"]

    # Update state
    state.agdp_eur += value_eur
    state.total_flops += r["flops"]

    # Record action
    state.actions.append(ActionRecord(
        kind="offline_ml",
        details={
            "baseline_acc": r["baseline_acc"],
            "acc": r["acc"],
            "improvement": r["improvement"],
            "n_samples": r.get("n_samples", 200),
            "n_features": r.get("n_features", 4)
        },
        flops=r["flops"],
        value_eur=value_eur
    ))

    return state


def tool_llm_real(state, prompt="Clean 100 latest rows to ISO schema."):
    """
    Execute real LLM job via Anthropic API.
    Measures tokens and FLOPs.
    """
    r = llm_job(prompt)

    # Check for errors
    if "error" in r:
        # Log error but don't add value
        state.actions.append(ActionRecord(
            kind="llm_job_failed",
            details={"error": r["error"], "message": r.get("message", "")},
            flops=0,
            value_eur=0.0
        ))
        return state

    # Compute value based on tokens and trust
    # rate: €/1k tokens (net margin to agent)
    rate = 0.8
    trust_mult = 0.8 + (state.trust_score / 1000) * 0.4
    value_eur = (r["tokens"] / 1000.0) * rate * trust_mult

    # Update state
    state.agdp_eur += value_eur
    state.total_flops += r["flops"]

    # Record action
    state.actions.append(ActionRecord(
        kind="llm_job",
        details={
            "tokens": r["tokens"],
            "tokens_in": r.get("tokens_in", 0),
            "tokens_out": r.get("tokens_out", 0),
            "model": r.get("model", "unknown"),
            "prompt_preview": prompt[:80]
        },
        flops=r["flops"],
        value_eur=value_eur
    ))

    return state


def tool_online_micro(state):
    """
    Online microtask: synthetic mini-task.
    (Kept for compatibility with existing graphs)
    """
    import numpy as np

    np.random.seed(42)
    n_micro = 100
    flops_per = 500
    value_per = 0.08

    total_flops = n_micro * flops_per
    total_value = n_micro * value_per

    state.agdp_eur += total_value
    state.total_flops += total_flops

    state.actions.append(ActionRecord(
        kind="online_micro",
        details={"n_tasks": n_micro, "flops_per": flops_per},
        flops=total_flops,
        value_eur=total_value
    ))

    return state


def tool_trust_rating(state):
    """
    Simple trust rating update based on performance.
    """
    # Increase trust if AGDP is positive
    if state.agdp_eur > 50:
        state.trust_score += 25
    elif state.agdp_eur > 20:
        state.trust_score += 10
    elif state.agdp_eur > 0:
        state.trust_score += 5

    # Cap at 1000
    state.trust_score = min(state.trust_score, 1000)

    state.actions.append(ActionRecord(
        kind="trust_update",
        details={"new_score": state.trust_score},
        flops=0,
        value_eur=0.0
    ))

    return state
