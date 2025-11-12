import os, json, statistics
from dotenv import load_dotenv; load_dotenv()
from langgraph.graph import StateGraph, END
from agents.state import GraphState
from agents.nodes import (
    node_identity, node_spawn, node_lend, node_producer, node_insurer,
    node_monetizer, node_delegate, node_accountant
)

def build_graph():
    g = StateGraph(GraphState)
    g.add_node("identity", node_identity)
    if os.getenv("ENABLE_SPAWN","false").lower()=="true": g.add_node("spawn", node_spawn)
    if os.getenv("ENABLE_LEND","false").lower()=="true": g.add_node("lend", node_lend)
    g.add_node("producer", node_producer)
    g.add_node("insurer", node_insurer)
    g.add_node("monetizer", node_monetizer)
    if os.getenv("ENABLE_DELEGATE","false").lower()=="true": g.add_node("delegate", node_delegate)
    g.add_node("accountant", node_accountant)

    g.set_entry_point("identity")
    cur="identity"
    if os.getenv("ENABLE_SPAWN","false").lower()=="true": g.add_edge(cur,"spawn"); cur="spawn"
    if os.getenv("ENABLE_LEND","false").lower()=="true": g.add_edge(cur,"lend"); cur="lend"
    g.add_edge(cur,"producer"); cur="producer"
    g.add_edge(cur,"insurer"); cur="insurer"
    g.add_edge(cur,"monetizer"); cur="monetizer"
    if os.getenv("ENABLE_DELEGATE","false").lower()=="true": g.add_edge(cur,"delegate"); cur="delegate"
    g.add_edge(cur,"accountant"); g.add_edge("accountant", END)
    return g.compile()

def summary(o: GraphState):
    print(json.dumps(o.model_dump(), indent=2))
    print("\nSUMMARY:")
    print(f"AGDP $={o.agdp_usd:.2f} | PFLOPs={o.total_flops/1e15:.6e} | GDP/PFLOP $={o.gdp_per_pflop_usd}")
    print(f"ComputeCost $={o.compute_cost_usd} | CRI={o.cri}")
    print(f"Premium={o.premium_usd} | Claim={o.claim_usd} | TakeRate={o.platform_revenue_usd}")
    print(f"Royalties={o.royalties_usd} | LoanRepay={o.loans_repaid_usd}")
    print(f"NET $={o.agent_net_usd} | PASSED={o.passed}")
    print(f"RECEIPT={o.receipt[:16]}… | SIG={(o.signature_b64 or '')[:12]}…")
    print(f"AnthropicUsageID={o.anthropic_usage_id} | StripePI={o.stripe_payment_intent_id}")

def run_once():
    app = build_graph()
    st = GraphState()
    result = app.invoke(st)
    if isinstance(result, dict):
        out = GraphState(**result)
    else:
        out = result
    summary(out)

def run_parallel(N=30):
    app = build_graph()
    nets, gdp_pflops, cris = [], [], []
    for _ in range(N):
        result = app.invoke(GraphState())
        if isinstance(result, dict):
            out = GraphState(**result)
        else:
            out = result
        nets.append(out.agent_net_usd)
        if out.gdp_per_pflop_usd is not None: gdp_pflops.append(out.gdp_per_pflop_usd)
        if out.cri is not None: cris.append(out.cri)
    p50_net = statistics.median(nets)
    p95_net = sorted(nets)[int(0.95*len(nets))-1]
    p50_cri = statistics.median(cris) if cris else None
    p95_gdpp = sorted(gdp_pflops)[int(0.95*len(gdp_pflops))-1] if gdp_pflops else None
    print(f"\nPARALLEL N={N}: p50(NET)={p50_net:.2f} | p95(NET)={p95_net:.2f} | p50(CRI)={p50_cri} | p95(GDP/PFLOP)={p95_gdpp}")

if __name__=="__main__":
    run_once()
    # run_parallel(30)
