import os
from .flops import real_or_synth
from .llm import llm_job
from .payments import stripe_capture
from .state import GraphState, ActionRecord
from .oracle import load_oracle

def tool_producer_oracle(state: GraphState)->GraphState:
    o = load_oracle()
    if not o: return state
    if o["override_agdp_usd"] is not None:
        value_usd = float(o["override_agdp_usd"]); delta = None
    else:
        delta = float(o["delta_kpi_pct"])
        value_usd = state.price_per_point * delta
    toks = int(o["tokens_used"])
    flops_log = 0
    if toks > 0:
        state.tokens_used += toks
        L, d = 48, 4096
        est_flops = int(6 * L * (d**2) * toks)
        state.total_flops += est_flops
        flops_log = est_flops
    state.agdp_usd += value_usd
    state.actions.append(ActionRecord(
        kind="oracle_kpi", details={"delta_kpi_pct": delta, "tokens_used": toks},
        flops=flops_log, value_usd=value_usd
    ))
    return state

def tool_producer_csv(state: GraphState)->GraphState:
    r = real_or_synth(price_per_point=state.price_per_point)
    state.baseline_acc = round(r["baseline_acc"],4)
    state.acc = round(r["acc"],4)
    state.improvement = round(r["improvement"],4)
    state.total_flops += r["flops"]
    state.agdp_usd += r["value_usd"]
    state.actions.append(ActionRecord(
        kind="offline_logreg",
        details={"baseline_acc":state.baseline_acc,"acc":state.acc,"improvement":state.improvement},
        flops=r["flops"], value_usd=r["value_usd"]
    ))
    return state

def tool_producer_llm(state: GraphState)->GraphState:
    res = llm_job("Clean and normalize the last 100 rows to the target schema.")
    if not res: return state
    state.tokens_used += res["tokens"]
    state.total_flops += res["flops"]
    rate_per_1k = 0.8
    trust_mult = 0.8 + (state.trust_score/1000)*0.4
    value_usd = (res["tokens"]/1000.0) * rate_per_1k * trust_mult
    state.agdp_usd += value_usd
    state.anthropic_usage_id = res.get("usage_id")
    state.actions.append(ActionRecord(
        kind="llm_job",
        details={"tokens":res["tokens"],"usage_id":state.anthropic_usage_id},
        flops=res["flops"], value_usd=value_usd
    ))
    return state

def tool_insurer(state: GraphState)->GraphState:
    return state

def tool_monetizer(state: GraphState)->GraphState:
    pi = stripe_capture(amount_usd=state.agdp_usd*state.take_rate, description=f"take-rate {state.run_id}")
    state.stripe_payment_intent_id = pi
    return state

def tool_spawn(state: GraphState)->GraphState:
    if os.getenv("ENABLE_SPAWN","false").lower()!="true": return state
    seed = state.spawn_params["seed_cost_usd"]; alpha = state.spawn_params["alpha"]
    child_trust = int(round(state.trust_score * alpha))
    state.vault_usd -= seed
    state.actions.append(ActionRecord(kind="spawn", details={"seed_cost":seed,"child_trust":child_trust}))
    return state

def tool_lend(state: GraphState)->GraphState:
    if os.getenv("ENABLE_LEND","false").lower()!="true": return state
    p = state.lend_params["principal_usd"]; base = state.lend_params["base"]; spread = state.lend_params["spread"]
    r = base + spread*(1 - state.trust_score/1000)
    due = round(p*(1+r),2)
    state.vault_usd += p
    state.loans.append({"principal":p,"r":r,"due":due})
    state.actions.append(ActionRecord(kind="lend_received", details={"principal":p,"r":round(r,4),"due":due}, value_usd=p))
    return state

def tool_delegate(state: GraphState)->GraphState:
    if os.getenv("ENABLE_DELEGATE","false").lower()!="true": return state
    fee = state.delegate_params["fee_usd"]; royalty = state.delegate_params["royalty"]; did = state.delegate_params["delegate_id"]
    state.delegators[did] = {"fee":fee, "royalty":royalty}
    state.vault_usd -= fee
    state.actions.append(ActionRecord(kind="delegate_open", details={"delegate_id":did,"fee":fee,"royalty":royalty}, value_usd=-fee))
    return state
